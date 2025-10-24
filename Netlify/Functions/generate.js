// This file is updated with the correct authentication header for Vertex AI

export default async (req, context) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  try {
    // 1. Get the secret variables from Netlify
    const apiKey = process.env.GEMINI_API_KEY;
    const projectId = process.env.GEMINI_PROJECT_ID;
    const region = process.env.GEMINI_PROJECT_REGION || 'us-central1';

    if (!apiKey || !projectId) {
      return new Response(JSON.stringify({ error: 'API key or Project ID is not configured on server.' }), { status: 500 });
    }

    // 2. Get the payload from the client (index.html)
    const payload = await req.json();

    // 3. Construct the Vertex AI URL
    const model = 'gemini-2.5-flash-preview-09-2025'; 
    const apiUrl = `https://generativelanguage.googleapis.com/v1/projects/${projectId}/locations/${region}/publishers/google/models/${model}:generateContent`;

    // 4. Call the Vertex AI API
    const geminiResponse = await fetch(`${apiUrl}?key=${apiKey}`, { // Corrected: API key as query param
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization' header removed
      },
      body: JSON.stringify(payload),
    });

    if (!geminiResponse.ok) {
      const errorBody = await geminiResponse.json(); // Use .json() to get the error details
      console.error('Vertex AI API Error:', errorBody);
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

