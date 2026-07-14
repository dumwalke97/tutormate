// Firebase ID tokens are verified against Google's public JWKS with `jose`,
// per Firebase's documented third-party JWT verification: signature, issuer,
// audience, expiry, and subject. No service account or firebase-admin needed.
// Same approach as generate.js, factored out so the Stripe functions share it.
export const FIREBASE_PROJECT_ID = 'tutor-mate-476113';
const FIREBASE_JWKS_URL =
  'https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com';

let jwks = null;
export async function verifyFirebaseToken(token) {
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

// Pulls the bearer token out of a Request's Authorization header, verifies
// it, and returns the decoded payload. Throws on anything missing/invalid so
// callers can respond 401 from a single catch block.
export async function requireFirebaseUser(req) {
  const authHeader = req.headers.get('authorization') || '';
  const tokenMatch = authHeader.match(/^Bearer (.+)$/);
  if (!tokenMatch) {
    throw new Error('Missing ID token');
  }
  const decodedToken = await verifyFirebaseToken(tokenMatch[1]);
  return { uid: decodedToken.sub, idToken: tokenMatch[1], decodedToken };
}
