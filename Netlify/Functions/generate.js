import admin from 'firebase-admin';

// Initialize Firebase Admin lazily so a missing/invalid env var produces a
// clear error response instead of crashing the function at load time.
let adminInitError = null;
function ensureAdmin() {
  if (admin.apps.length) return true;
  try {
    admin.initializeApp({
      credential: admin.credential.cert(
        JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT)
      ),
    });
    return true;
  } catch (initError) {
    adminInitError = initError;
    return false;
  }
}

export default async (req, context) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  // 0. Require a valid Firebase ID token before doing anything else.
  if (!ensureAdmin()) {
    console.error('Firebase Admin init failed (is FIREBASE_SERVICE_ACCOUNT set in Netlify env vars?):', adminInitError);
    return new Response(JSON.stringify({ error: 'Server auth is not configured.' }), { status: 500 });
  }

  const authHeader = req.headers.get('authorization') || '';
  const tokenMatch = authHeader.match(/^Bearer (.+)$/);
  if (!tokenMatch) {
    return new Response(JSON.stringify({ error: 'Missing ID token' }), { status: 401 });
  }

  let decodedToken;
  try {
    decodedToken = await admin.auth().verifyIdToken(tokenMatch[1]);
  } catch (authError) {
    console.error('Token verification failed:', authError);
    return new Response(JSON.stringify({ error: 'Invalid or expired ID token' }), { status: 401 });
  }
  // decodedToken.uid identifies the caller (useful for rate limiting/logging).

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

    // 5. Send the successful response back to index.html
    const data = await geminiResponse.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in Netlify function:', error);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
};
