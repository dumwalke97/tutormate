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

// Sentinel meaning "Gemini hasn't sent response headers yet" — see the race in
// step 4. A unique symbol so it can never collide with a real Response.
const SLOW = Symbol('gemini-headers-pending');

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
    return { usageCount: 0, subscriptionStatus: null, appleSubscriptionStatus: null, subscriptionSource: null };
  }
  if (!res.ok) {
    throw new Error(`Failed to read usage (status ${res.status})`);
  }
  const doc = await res.json();
  const usageCount = parseInt(doc.fields?.usageCount?.integerValue || '0', 10);
  const subscriptionStatus = doc.fields?.subscriptionStatus?.stringValue || null;
  // Written by the iOS app when a subscription is purchased through Apple.
  // Same login, either platform: an Apple subscription unlocks the web too.
  const appleSubscriptionStatus = doc.fields?.appleSubscriptionStatus?.stringValue || null;
  const subscriptionSource = doc.fields?.subscriptionSource?.stringValue || null;
  return { usageCount, subscriptionStatus, appleSubscriptionStatus, subscriptionSource };
}

// A user is subscribed if either purchase path is active: Stripe on the web
// (subscriptionStatus, written by the Stripe webhook — also 'active' for
// grandfathered accounts) or Apple on iOS (appleSubscriptionStatus).
function isSubscribedUsage(usage) {
  return usage.subscriptionStatus === 'active' || usage.appleSubscriptionStatus === 'active';
}

// Where the active subscription came from, for the client's "manage
// subscription" affordance ('grandfathered' | 'stripe' | 'apple' | null).
function subscriptionSourceOf(usage) {
  if (usage.subscriptionSource) return usage.subscriptionSource;
  if (usage.subscriptionStatus === 'active') return 'stripe';
  if (usage.appleSubscriptionStatus === 'active') return 'apple';
  return null;
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
  let usage = { usageCount: 0, subscriptionStatus: null, appleSubscriptionStatus: null, subscriptionSource: null };
  if (isWebClient) {
    try {
      usage = await getUsage(uid, idToken);
    } catch (usageError) {
      console.error('Usage lookup failed:', usageError);
      // Fail open on lookup errors so a Firestore hiccup doesn't block a
      // paying/free user entirely; the increment below will still be attempted.
    }

    const isSubscribed = isSubscribedUsage(usage);
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

    // 3. Construct the correct Gemini API URL.
    //
    // We call the STREAMING endpoint (`streamGenerateContent?alt=sse`) rather
    // than `generateContent`, for a reason that has nothing to do with wanting
    // token-by-token output: the edge in front of these functions enforces a
    // ~30s *inactivity* timeout ("Too much time has passed without sending any
    // data for document") and kills the connection with a 504. A buffered call
    // sends zero bytes while Gemini thinks, so any generation slower than ~30s
    // — long quizzes, and especially multi-page homework photos — died there.
    // Streaming lets us emit bytes continuously (see `keepAlive` below), which
    // resets that timer and removes the ceiling entirely.
    const model = 'gemini-3.6-flash';
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent`;

    // 4. Call the Gemini API.
    //
    // `fetch` resolves when the response HEADERS arrive — but Gemini can spend
    // a long time reading an image before it emits anything at all (measured:
    // 27–31s time-to-first-byte for a dense handwritten worksheet + a 50
    // question quiz). Awaiting that outright would send zero bytes for the
    // whole window and trip the same ~30s inactivity timeout we're trying to
    // avoid, so we race the headers against a deadline that lands safely
    // inside it:
    //
    //   • headers back before the deadline (the usual case) — behave exactly
    //     as a normal request and keep real HTTP error statuses;
    //   • still waiting at the deadline — open the keep-alive stream *now*,
    //     before the guillotine, and finish the work inside it.
    const HEADERS_DEADLINE_MS = 20000;
    const geminiRequest = fetch(`${apiUrl}?alt=sse&key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    let deadlineTimer;
    const deadline = new Promise((resolve) => {
      deadlineTimer = setTimeout(() => resolve(SLOW), HEADERS_DEADLINE_MS);
    });
    // Capture a rejection as a value rather than letting it escape the race —
    // the stream below awaits this same promise and would otherwise trigger an
    // unhandled rejection.
    const raced = await Promise.race([
      geminiRequest.then((r) => r, (requestError) => ({ requestError })),
      deadline,
    ]);
    clearTimeout(deadlineTimer);

    // Fast path: we know the outcome before committing to a 200, so any
    // failure can still be surfaced with a real HTTP error status.
    if (raced !== SLOW) {
      if (raced.requestError) throw raced.requestError;
      if (!raced.ok) {
        const errorBody = await raced.json().catch(() => ({}));
        console.error('Gemini API Error:', JSON.stringify(errorBody, null, 2));
        // Pass the specific error message from the API back to the client
        const errorMessage = errorBody.error?.message || `API request failed with status ${raced.status}`;
        throw new Error(errorMessage);
      }
    }

    // 5. Reassemble the SSE stream into the single response shape both clients
    // already expect, while trickling whitespace to hold the connection open.
    // JSON parsers ignore leading whitespace (verified on Swift's JSONDecoder
    // and browser JSON.parse), so this needs no client-side change.
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const ping = () => {
          try { controller.enqueue(encoder.encode(' ')); } catch { /* already closed */ }
        };
        // Belt and braces: Gemini's own chunks usually keep us well under the
        // limit, but this covers any long pause before or between them.
        let keepAlive = setInterval(ping, 3000);
        const stopKeepAlive = () => {
          if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
        };

        try {
          // On the slow path the headers still haven't landed; keep-alive is
          // already running, so it's safe to wait for them here.
          const geminiResponse = raced === SLOW ? await geminiRequest : raced;
          if (!geminiResponse.ok) {
            const errorBody = await geminiResponse.json().catch(() => ({}));
            console.error('Gemini API Error:', JSON.stringify(errorBody, null, 2));
            throw new Error(
              errorBody.error?.message || `API request failed with status ${geminiResponse.status}`
            );
          }

          const reader = geminiResponse.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';
          let fullText = '';
          let lastChunk = null;

          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            ping(); // real activity from Gemini also resets the timer
            buffer += decoder.decode(value, { stream: true });

            let newlineIndex;
            while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
              const line = buffer.slice(0, newlineIndex).trim();
              buffer = buffer.slice(newlineIndex + 1);
              if (!line.startsWith('data:')) continue;
              const jsonStr = line.slice(5).trim();
              if (!jsonStr || jsonStr === '[DONE]') continue;
              try {
                const chunk = JSON.parse(jsonStr);
                lastChunk = chunk;
                const parts = chunk?.candidates?.[0]?.content?.parts;
                if (Array.isArray(parts)) {
                  fullText += parts.map((p) => p.text || '').join('');
                }
              } catch {
                // A partial line can't be parsed yet; the next read completes it.
              }
            }
          }

          stopKeepAlive();

          const data = {
            candidates: [
              {
                content: { parts: [{ text: fullText }] },
                finishReason: lastChunk?.candidates?.[0]?.finishReason ?? null,
              },
            ],
            usageMetadata: lastChunk?.usageMetadata ?? null,
          };

          // Web only: spend a free credit on a successful generation, and
          // attach updated usage info so the UI can show "X of 10 free uses
          // left". Skipped entirely for the iOS app (see isWebClient above).
          if (isWebClient) {
            const newUsageCount = usage.usageCount + 1;
            await incrementUsage(uid, idToken, newUsageCount);
            data._usage = {
              count: newUsageCount,
              limit: FREE_LIMIT,
              subscribed: isSubscribedUsage(usage),
              subscriptionSource: subscriptionSourceOf(usage),
            };
          }

          controller.enqueue(encoder.encode(JSON.stringify(data)));
          controller.close();
        } catch (streamError) {
          // The 200 and some whitespace are already on the wire by now, so the
          // status can't be changed; surface the failure in the body instead.
          stopKeepAlive();
          console.error('Error streaming from Gemini:', streamError);
          try {
            controller.enqueue(encoder.encode(JSON.stringify({ error: streamError.message })));
            controller.close();
          } catch { /* already closed */ }
        }
      },
    });

    return new Response(stream, {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in Netlify function:', error);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
};
