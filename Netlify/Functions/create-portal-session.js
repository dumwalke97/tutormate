// Opens Stripe's hosted Customer Portal so subscribers can update payment
// methods, switch plans, or cancel without any of that UI living in our app.
import Stripe from 'stripe';
import { requireFirebaseUser } from './lib/firebaseAuth.js';
import { getUserDocAdmin } from './lib/firestoreAdmin.js';

export default async (req) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  let uid;
  try {
    ({ uid } = await requireFirebaseUser(req));
  } catch (authError) {
    console.error('Token verification failed:', authError);
    return new Response(JSON.stringify({ error: 'Invalid or expired ID token' }), { status: 401 });
  }

  const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
  if (!stripeSecretKey) {
    return new Response(JSON.stringify({ error: 'Stripe is not configured on the server.' }), { status: 500 });
  }
  const stripe = new Stripe(stripeSecretKey);

  try {
    const { stripeCustomerId } = await getUserDocAdmin(uid);
    if (!stripeCustomerId) {
      return new Response(JSON.stringify({ error: 'No subscription found for this account.' }), { status: 400 });
    }

    const origin = req.headers.get('origin') || new URL(req.url).origin;
    const portalSession = await stripe.billingPortal.sessions.create({
      customer: stripeCustomerId,
      return_url: `${origin}/app/`,
    });

    return new Response(JSON.stringify({ url: portalSession.url }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error creating portal session:', error);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
};
