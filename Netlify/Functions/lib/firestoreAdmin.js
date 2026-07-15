// Privileged Firestore access for fields a user's own ID token isn't trusted
// to write (subscriptionStatus, stripeCustomerId, stripeSubscriptionId).
// Exchanges the GCP_SERVICE_ACCOUNT_KEY service account for a short-lived
// Google OAuth2 access token (JWT-bearer flow), then talks to the Firestore
// REST API directly — no firebase-admin dependency, matching the rest of
// this codebase's approach (see generate.js).
import { FIREBASE_PROJECT_ID } from './firebaseAuth.js';

const FIRESTORE_BASE = `https://firestore.googleapis.com/v1/projects/${FIREBASE_PROJECT_ID}/databases/(default)/documents`;
const TOKEN_URL = 'https://oauth2.googleapis.com/token';
const SCOPE = 'https://www.googleapis.com/auth/datastore';

let cachedToken = null; // { accessToken, expiresAt }

async function getAccessToken() {
  if (cachedToken && cachedToken.expiresAt > Date.now() + 60_000) {
    return cachedToken.accessToken;
  }

  const keyJson = process.env.GCP_SERVICE_ACCOUNT_KEY;
  if (!keyJson) {
    throw new Error('GCP_SERVICE_ACCOUNT_KEY is not configured on the server.');
  }
  const serviceAccount = JSON.parse(keyJson);

  const { SignJWT, importPKCS8 } = await import('jose');
  const privateKey = await importPKCS8(serviceAccount.private_key, 'RS256');

  const now = Math.floor(Date.now() / 1000);
  const assertion = await new SignJWT({ scope: SCOPE })
    .setProtectedHeader({ alg: 'RS256' })
    .setIssuer(serviceAccount.client_email)
    .setAudience(TOKEN_URL)
    .setIssuedAt(now)
    .setExpirationTime(now + 3600)
    .sign(privateKey);

  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to exchange service account for access token (status ${res.status}): ${await res.text()}`);
  }
  const { access_token, expires_in } = await res.json();
  cachedToken = { accessToken: access_token, expiresAt: Date.now() + expires_in * 1000 };
  return access_token;
}

// Converts a flat { key: 'value' } object into Firestore's typed field
// format. Only strings are needed by the Stripe functions so that's all
// this supports.
function toFirestoreFields(fields) {
  const out = {};
  for (const [key, value] of Object.entries(fields)) {
    out[key] = value === null ? { nullValue: null } : { stringValue: String(value) };
  }
  return out;
}

// Reads users/{uid} with admin credentials (bypasses Security Rules).
// Returns {} for a document that doesn't exist yet.
export async function getUserDocAdmin(uid) {
  const accessToken = await getAccessToken();
  const res = await fetch(`${FIRESTORE_BASE}/users/${uid}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (res.status === 404) {
    return {};
  }
  if (!res.ok) {
    throw new Error(`Failed to read users/${uid} (status ${res.status}): ${await res.text()}`);
  }
  const doc = await res.json();
  const fields = doc.fields || {};
  return {
    stripeCustomerId: fields.stripeCustomerId?.stringValue || null,
    stripeSubscriptionId: fields.stripeSubscriptionId?.stringValue || null,
    subscriptionStatus: fields.subscriptionStatus?.stringValue || null,
  };
}

// Lists every users/{uid} doc with admin credentials, paginating through
// the whole collection. Used by one-off migration scripts, not by any
// deployed function — there's no reason a request handler should ever need
// to enumerate every user.
export async function listAllUsersAdmin() {
  const accessToken = await getAccessToken();
  const results = [];
  let pageToken;
  do {
    const url = new URL(`${FIRESTORE_BASE}/users`);
    url.searchParams.set('pageSize', '300');
    if (pageToken) url.searchParams.set('pageToken', pageToken);
    const res = await fetch(url, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!res.ok) {
      throw new Error(`Failed to list users (status ${res.status}): ${await res.text()}`);
    }
    const data = await res.json();
    for (const doc of data.documents || []) {
      const fields = doc.fields || {};
      results.push({
        uid: doc.name.split('/').pop(),
        stripeCustomerId: fields.stripeCustomerId?.stringValue || null,
        subscriptionStatus: fields.subscriptionStatus?.stringValue || null,
      });
    }
    pageToken = data.nextPageToken;
  } while (pageToken);
  return results;
}

// Upserts the given string fields on users/{uid} with admin credentials.
// Firestore's PATCH with updateMask creates the document if it doesn't
// exist yet, so this works for a brand-new user too.
export async function setUserFieldsAdmin(uid, fields) {
  const accessToken = await getAccessToken();
  const fieldPaths = Object.keys(fields).map((key) => `updateMask.fieldPaths=${encodeURIComponent(key)}`).join('&');
  const url = `${FIRESTORE_BASE}/users/${uid}?${fieldPaths}`;
  const res = await fetch(url, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ fields: toFirestoreFields(fields) }),
  });
  if (!res.ok) {
    throw new Error(`Failed to update users/${uid} (status ${res.status}): ${await res.text()}`);
  }
}
