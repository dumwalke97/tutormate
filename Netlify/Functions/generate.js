// This file is updated to use the correct "Gemini API" (generativelanguage) endpoint.
import { GoogleAuth } from 'google-auth-library';


export default async (req, context) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  try {
    // 1. Get the secret variables from Netlify
    const serviceAccountKey = process.env.GCP_SERVICE_ACCOUNT_KEY;
    const projectId = process.env.GEMINI_PROJECT_ID; // Your Google Cloud Project ID
    const region = process.env.GEMINI_PROJECT_REGION; // Your Google Cloud Region

    if (!serviceAccountKey || !projectId || !region) {
      return new Response(JSON.stringify({ error: 'Service Account, Project ID, or Region is not configured on server.' }), { status: 500 });
    }

    // 2. Get the payload from the client (index.html)
    const { model, geminiPayload } = await req.json();

    if (!model || !geminiPayload) {
      return new Response(JSON.stringify({ error: 'Request body must include "model" and "geminiPayload".' }), { status: 400 });
    }

    // 3. Construct the correct Gemini API URL
    // The latest models use the aiplatform endpoint, which requires project ID and region.
    const apiUrl = `https://${region}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${region}/publishers/google/models/${model}:generateContent`;

    // 4. Authenticate using the service account to get an access token
    const auth = new GoogleAuth({
      credentials: JSON.parse(serviceAccountKey),
      scopes: 'https://www.googleapis.com/auth/cloud-platform'
    });
    const client = await auth.getClient();

    // 5. Call the Gemini API using the authenticated client
    // The google-auth-library's client automatically handles the Authorization header and parses the JSON response.
    const geminiResponse = await client.request({
      url: apiUrl,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(geminiPayload),
    });

    // The response object from client.request() is different from a standard fetch response.
    // The status is in geminiResponse.status and the data is in geminiResponse.data.
    if (geminiResponse.status !== 200) {
      console.error('Gemini API Error:', geminiResponse.data);
      // Pass the specific error message from the API back to the client
      const errorMessage = geminiResponse.data.error?.message || `API request failed with status ${geminiResponse.status}`;
      throw new Error(errorMessage);
    }

    // 6. Send the successful response back to index.html
    // The data is already a parsed JSON object in geminiResponse.data
    return new Response(JSON.stringify(geminiResponse.data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in Netlify function:', error);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
};
