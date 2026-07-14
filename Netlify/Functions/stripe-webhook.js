// Source of truth for subscriptionStatus. Stripe calls this directly (no
// Firebase ID token involved), so every write here uses the service-account
// admin path — never the caller's own token, since there isn't one.
import Stripe from 'stripe';
import { setUserFieldsAdmin } from './lib/firestoreAdmin.js';

async function writeSubscriptionState(uid, subscription) {
  if (!uid) {
    console.warn(`Stripe subscription ${subscription.id} has no firebaseUID in metadata; skipping.`);
    return;
  }
  await setUserFieldsAdmin(uid, {
    subscriptionStatus: subscription.status,
    stripeSubscriptionId: subscription.id,
  });
}

export default async (req) => {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405 });
  }

  const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!stripeSecretKey || !webhookSecret) {
    return new Response(JSON.stringify({ error: 'Stripe is not configured on the server.' }), { status: 500 });
  }
  const stripe = new Stripe(stripeSecretKey);

  // Signature verification needs the exact raw body, so this must be read
  // as text before any JSON parsing.
  const rawBody = await req.text();
  const signature = req.headers.get('stripe-signature');

  let event;
  try {
    event = await stripe.webhooks.constructEventAsync(rawBody, signature, webhookSecret);
  } catch (signatureError) {
    console.error('Stripe webhook signature verification failed:', signatureError);
    return new Response(JSON.stringify({ error: 'Invalid signature' }), { status: 400 });
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object;
        if (session.mode === 'subscription' && session.subscription) {
          const uid = session.client_reference_id || session.metadata?.firebaseUID;
          const subscription = await stripe.subscriptions.retrieve(session.subscription);
          await writeSubscriptionState(uid, subscription);
        }
        break;
      }
      case 'customer.subscription.updated': {
        const subscription = event.data.object;
        await writeSubscriptionState(subscription.metadata?.firebaseUID, subscription);
        break;
      }
      case 'customer.subscription.deleted': {
        const subscription = event.data.object;
        await writeSubscriptionState(subscription.metadata?.firebaseUID, { ...subscription, status: 'canceled' });
        break;
      }
      default:
        break; // Not an event we act on.
    }
  } catch (handlingError) {
    console.error(`Error handling Stripe event ${event.type}:`, handlingError);
    return new Response(JSON.stringify({ error: 'Webhook handler failed' }), { status: 500 });
  }

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
