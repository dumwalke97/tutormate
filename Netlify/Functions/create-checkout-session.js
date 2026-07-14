// Creates a Stripe-hosted Checkout Session for a subscription and hands the
// client its URL to redirect to. Card details never touch our servers.
import Stripe from 'stripe';
import { requireFirebaseUser } from './lib/firebaseAuth.js';
import { getUserDocAdmin, setUserFieldsAdmin } from './lib/firestoreAdmin.js';

const PRICE_IDS = {
  monthly: process.env.STRIPE_PRICE_MONTHLY,
  annual: process.env.STRIPE_PRICE_ANNUAL,
};

export default async (req) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  let uid, decodedToken;
  try {
    ({ uid, decodedToken } = await requireFirebaseUser(req));
  } catch (authError) {
    console.error('Token verification failed:', authError);
    return new Response(JSON.stringify({ error: 'Invalid or expired ID token' }), { status: 401 });
  }

  // Anonymous (guest) sessions aren't a stable identity to attach a paid
  // subscription to — the frontend already blocks this, this is a backstop.
  if (decodedToken.firebase?.sign_in_provider === 'anonymous') {
    return new Response(
      JSON.stringify({ error: 'Please create an account or log in before subscribing.' }),
      { status: 403 }
    );
  }

  const { plan } = await req.json().catch(() => ({}));
  const priceId = PRICE_IDS[plan];
  if (!priceId) {
    return new Response(JSON.stringify({ error: 'Unknown plan. Expected "monthly" or "annual".' }), { status: 400 });
  }

  const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
  if (!stripeSecretKey) {
    return new Response(JSON.stringify({ error: 'Stripe is not configured on the server.' }), { status: 500 });
  }
  const stripe = new Stripe(stripeSecretKey);

  try {
    let { stripeCustomerId } = await getUserDocAdmin(uid);
    if (!stripeCustomerId) {
      const customer = await stripe.customers.create({
        email: decodedToken.email,
        metadata: { firebaseUID: uid },
      });
      stripeCustomerId = customer.id;
      await setUserFieldsAdmin(uid, { stripeCustomerId });
    }

    const origin = req.headers.get('origin') || new URL(req.url).origin;
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      customer: stripeCustomerId,
      line_items: [{ price: priceId, quantity: 1 }],
      client_reference_id: uid,
      subscription_data: { metadata: { firebaseUID: uid } },
      success_url: `${origin}/app/?checkout=success`,
      cancel_url: `${origin}/app/?checkout=cancel`,
    });

    return new Response(JSON.stringify({ url: session.url }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
};
