// Serves the Firebase web config to index.html. Uses the modern Netlify
// Functions API (not Lambda compatibility mode), which also avoids AWS
// Lambda's 4KB environment variable limit.
export default async (req, context) => {
  return new Response(
    JSON.stringify({
      firebaseApiKey: process.env.VITE_FIREBASE_API_KEY,
      firebaseAuthDomain: process.env.VITE_FIREBASE_AUTH_DOMAIN,
      firebaseProjectId: process.env.VITE_FIREBASE_PROJECT_ID,
      firebaseStorageBucket: process.env.VITE_FIREBASE_STORAGE_BUCKET,
      firebaseMessagingSenderId: process.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
      firebaseAppId: process.env.VITE_FIREBASE_APP_ID,
      firebaseMeasurementId: process.env.VITE_FIREBASE_MEASUREMENT_ID
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
};
