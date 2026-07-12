// Firebase ID tokens are verified against Google's public JWKS with `jose`,
// per Firebase's documented third-party JWT verification: signature, issuer,
// audience, expiry, and subject. No service account or firebase-admin needed.
// `jose` is ESM-only, so it's loaded via dynamic import (safe from the CJS
// output Netlify's bundler produces).
const FIREBASE_PROJECT_ID = 'tutor-mate-476113';
const FIREBASE_JWKS_URL =
  'https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com';

// Freemium cap: total assignment checks + quiz generations, combined, before
// a subscription is required. Matches the iOS app's free tier.
const FREE_LIMIT = 10;
const FIRESTORE_BASE = `https://firestore.googleapis.com/v1/projects/${FIREBASE_PROJECT_ID}/databases/(default)/documents`;

let jwks = null;
async function verifyFirebaseToken(token) {
  const { createRemoteJWKSet, jwtVerify } = await import('jose');
  if (!jwks) {
    jwks = createRemoteJWKSet(new URL(FIREBASE_JWKS_URL));
  }
  const { payload } = await jwtVerify(token, jwks, {
    issuer: `https://securetoken.google.com/${FIREBASE_PROJECT_ID}`,
    audience: FIREBASE_PROJECT_ID,
    algorithms: ['RS256'],
  });
  if (!payload.sub) {
    throw new Error('Token has no subject (uid).');
  }
  return payload;
}

// Reads users/{uid} using the caller's own Firebase ID token, so Firestore
// Security Rules (owner-only read/write) apply exactly as they would to a
// direct client call — no service account or elevated credentials needed.
async function getUsage(uid, idToken) {
  const res = await fetch(`${FIRESTORE_BASE}/users/${uid}`, {
    headers: { Authorization: `Bearer ${idToken}` },
  });
  if (res.status === 404) {
    return { usageCount: 0, subscriptionStatus: null };
  }
  if (!res.ok) {
    throw new Error(`Failed to read usage (status ${res.status})`);
  }
  const doc = await res.json();
  const usageCount = parseInt(doc.fields?.usageCount?.integerValue || '0', 10);
  const subscriptionStatus = doc.fields?.subscriptionStatus?.stringValue || null;
  return { usageCount, subscriptionStatus };
}

// Upserts usageCount only (never touches subscriptionStatus, which is
// reserved for the Stripe webhook writing with admin credentials).
async function incrementUsage(uid, idToken, newCount) {
  const url = `${FIRESTORE_BASE}/users/${uid}?updateMask.fieldPaths=usageCount`;
  const res = await fetch(url, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${idToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ fields: { usageCount: { integerValue: newCount } } }),
  });
  if (!res.ok) {
    // Don't fail the whole request just because the usage counter couldn't
    // be updated — log it and let the user keep their result.
    console.error('Failed to update usage count:', await res.text());
  }
}

export default async (req, context) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  // 0. Require a valid Firebase ID token before doing anything else.
  const authHeader = req.headers.get('authorization') || '';
  const tokenMatch = authHeader.match(/^Bearer (.+)$/);
  if (!tokenMatch) {
    return new Response(JSON.stringify({ error: 'Missing ID token' }), { status: 401 });
  }

  let decodedToken;
  try {
    decodedToken = await verifyFirebaseToken(tokenMatch[1]);
  } catch (authError) {
    console.error('Token verification failed:', authError);
    return new Response(JSON.stringify({ error: 'Invalid or expired ID token' }), { status: 401 });
  }
  // decodedToken.sub is the caller's uid, used both for logging and for the
  // free-tier usage cap below.
  const uid = decodedToken.sub;
  const idToken = tokenMatch[1];

  // 0.5. Enforce the web free tier before doing anything expensive. The count
  // is read fresh from Firestore on every call (never trusted from the
  // client), so this can't be bypassed by calling this endpoint directly.
  //
  // IMPORTANT: this gate only applies to calls from the website. The iOS app
  // enforces its own free-use limit locally (see UsageTracker.swift, backed
  // by StoreKit for subscription status) and never writes to this Firestore
  // field, so gating it here too would double-count and eventually block
  // paying iOS subscribers. The web client sends X-TutorMate-Platform: web;
  // the iOS app doesn't send this header, so it skips this block entirely
  // and behaves exactly as it did before this change.
  const isWebClient = req.headers.get('x-tutormate-platform') === 'web';
  let usage = { usageCount: 0, subscriptionStatus: null };
  if (isWebClient) {
    try {
      usage = await getUsage(uid, idToken);
    } catch (usageError) {
      console.error('Usage lookup failed:', usageError);
      // Fail open on lookup errors so a Firestore hiccup doesn't block a
      // paying/free user entirely; the increment below will still be attempted.
    }

    const isSubscribed = usage.subscriptionStatus === 'active';
    if (!isSubscribed && usage.usageCount >= FREE_LIMIT) {
      return new Response(
        JSON.stringify({
          error: 'FREE_LIMIT_REACHED',
          message: `You've used all ${FREE_LIMIT} free assignment checks and quizzes.`,
          usageCount: usage.usageCount,
          limit: FREE_LIMIT,
        }),
        { status: 402, headers: { 'Content-Type': 'application/json' } }
      );
    }
  }

  try {
    // 1. Get the secret variables from Netlify
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return new Response(JSON.stringify({ error: 'API key is not configured on server.' }), { status: 500 });
    }

    // 2. Get the payload from the client (index.html)
    const payload = await req.json();

    // --- New Logic to Handle fileUris ---
    // Before sending to Gemini, check if we need to fetch any images from URLs.
    if (payload.contents && payload.contents[0] && payload.contents[0].parts) {
      const parts = payload.contents[0].parts;

      // Use Promise.all to handle all asynchronous fetch operations concurrently.
      const processedParts = await Promise.all(parts.map(async (part) => {
        // If the part has a fileUri that is an HTTP URL, process it.
        if (part.fileData && part.fileData.fileUri && part.fileData.fileUri.startsWith('http')) {
          try {
            console.log(`Downloading image from URL: ${part.fileData.fileUri}`);
            const imageUrl = part.fileData.fileUri;
            const imageResponse = await fetch(imageUrl);
            if (!imageResponse.ok) {
              throw new Error(`Failed to fetch image from ${imageUrl}: ${imageResponse.statusText}`);
            }
            // Get the image data as a buffer and convert it to base64.
            const arrayBuffer = await imageResponse.arrayBuffer();
            const buffer = Buffer.from(arrayBuffer);
            const base64String = buffer.toString('base64');

            // Return a new part object in the format Gemini expects for inline data.
            // We use the mimeType from the payload or default to jpeg.
            return {
                inlineData: {
                    mimeType: part.fileData.mimeType || 'image/jpeg',
                    data: base64String
                }
            };
          } catch (fetchError) {
            console.error('Error fetching fileUri:', fetchError);
            // Return null for failed fetches so we can filter them out
            return null;
          }
        }
        return part; // If it's not a fileUri part (e.g., text or already inlineData), return it as is.
      }));

      // Replace the original parts with the processed ones, filtering out any nulls from failed fetches.
      payload.contents[0].parts = processedParts.filter(Boolean);

      if (payload.contents[0].parts.length === 0) {
           throw new Error("No valid content to send to AI (all file downloads failed).");
      }
    }

    // 3. Construct the correct Gemini API URL
    // This is the simple, correct URL for the API you enabled.
    // It does not use project ID or region.
    // Using the model you had in your uploaded file:
    const model = 'gemini-2.5-flash';
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

    // 4. Call the Gemini API
    const geminiResponse = await fetch(`${apiUrl}?key=${apiKey}`, { // API key as query param
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!geminiResponse.ok) {
      const errorBody = await geminiResponse.json(); // Use .json() to get the error details
      console.error('Gemini API Error:', JSON.stringify(errorBody, null, 2));
      // Pass the specific error message from the API back to the client
      const errorMessage = errorBody.error?.message || `API request failed with status ${geminiResponse.status}`;
      throw new Error(errorMessage);
    }

    // 5. Web only: spend a free credit on a successful generation, and
    // attach updated usage info so the UI can show "X of 10 free uses left".
    // Skipped entirely for the iOS app (see the isWebClient check above).
    const data = await geminiResponse.json();
    if (isWebClient) {
      const newUsageCount = usage.usageCount + 1;
      await incrementUsage(uid, idToken, newUsageCount);
      data._usage = {
        count: newUsageCount,
        limit: FREE_LIMIT,
        subscribed: usage.subscriptionStatus === 'active',
      };
    }
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in Netlify function:', error);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
};
