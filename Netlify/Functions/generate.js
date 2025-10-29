// This file is updated to use the correct "Gemini API" (generativelanguage) endpoint.

export default async (req, context) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  try {
    // 1. Get the secret variables from Netlify
    // 1. Get the secret variables from Netlify environment
    const apiKey = process.env.GEMINI_API_KEY; // Your Gemini API Key
    const projectId = process.env.GEMINI_PROJECT_ID; // Your Google Cloud Project ID
    const region = process.env.GEMINI_PROJECT_REGION; // Your Google Cloud Region

    if (!apiKey || !projectId || !region) {
      return new Response(JSON.stringify({ error: 'API key, Project ID, or Region is not configured on server.' }), { status: 500 });
    }

    // 2. Get the payload from the client (index.html)
    const { model, geminiPayload } = await req.json();

    if (!model || !geminiPayload) {
      return new Response(JSON.stringify({ error: 'Request body must include "model" and "geminiPayload".' }), { status: 400 });
    }

    // 3. Construct the correct Gemini API URL
    // The latest models use the aiplatform endpoint, which requires project ID and region.
    const apiUrl = `https://${region}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${region}/publishers/google/models/${model}:streamGenerateContent`;

    // 4. Call the Gemini API
    // The API key is now passed as an Authorization header for this endpoint.
    const geminiResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(geminiPayload),
    });

    if (!geminiResponse.ok) {
      const errorBody = await geminiResponse.json(); // Use .json() to get the error details
      console.error('Gemini API Error:', errorBody);
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
