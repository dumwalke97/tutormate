// This file is our secure "backend."
// It runs on Netlify's servers, not in the user's browser.

export default async (req, context) => {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  try {
    // 1. Get the secret API key from Netlify's secure storage
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      // This error will appear if you forget Step 4
      return new Response(JSON.stringify({ error: 'API key is not configured on server.' }), { status: 500 });
    }

    // 2. Get the payload (prompts, images) sent from the index.html file
    const payload = await req.json();
    
    // 3. Call the Gemini API, adding the secret key on the server
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`;

    const geminiResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload), // Pass the client's payload to Gemini
    });

    if (!geminiResponse.ok) {
      const errorBody = await geminiResponse.text();
      console.error('Gemini API Error:', errorBody);
      throw new Error(`Gemini API request failed with status ${geminiResponse.status}`);
    }

    // 4. Send the successful response from Gemini back to the index.html file
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

