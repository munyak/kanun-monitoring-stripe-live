/**
 * KaNun Monitoring — Stripe Webhook Handler
 * Netlify Function: /api/webhooks/stripe
 * 
 * Handles events:
 * - checkout.session.completed
 * - customer.subscription.created
 * - customer.subscription.updated
 * - customer.subscription.deleted
 * - invoice.payment_succeeded
 * - invoice.payment_failed
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Webhook signing secret (from Stripe Dashboard > Developers > Webhooks)
const WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET;

exports.handler = async (event, context) => {
  const sig = event.headers['stripe-signature'];

  // Verify webhook signature
  let stripeEvent;
  try {
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      WEBHOOK_SECRET
    );
  } catch (error) {
    console.error('Webhook signature verification failed:', error.message);
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Invalid signature' }),
    };
  }

  console.log(`Received Stripe event: ${stripeEvent.type}`);

  try {
    // Handle different event types
    switch (stripeEvent.type) {
      case 'checkout.session.completed':
        await handleCheckoutSessionCompleted(stripeEvent.data.object);
        break;

      case 'customer.subscription.created':
        await handleSubscriptionCreated(stripeEvent.data.object);
        break;

      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(stripeEvent.data.object);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(stripeEvent.data.object);
        break;

      case 'invoice.payment_succeeded':
        await handleInvoicePaymentSucceeded(stripeEvent.data.object);
        break;

      case 'invoice.payment_failed':
        await handleInvoicePaymentFailed(stripeEvent.data.object);
        break;

      default:
        console.log(`Unhandled event type: ${stripeEvent.type}`);
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ received: true }),
    };
  } catch (error) {
    console.error('Webhook processing error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Webhook processing failed' }),
    };
  }
};

// ========================================================================
// EVENT HANDLERS
// ========================================================================

async function handleCheckoutSessionCompleted(session) {
  console.log('✓ Checkout session completed:', {
    sessionId: session.id,
    customerId: session.customer,
    email: session.customer_email,
  });

  // TODO: Save customer to database
  // TODO: Send welcome email
  // TODO: Activate account
}

async function handleSubscriptionCreated(subscription) {
  console.log('✓ Subscription created:', {
    subscriptionId: subscription.id,
    customerId: subscription.customer,
    status: subscription.status,
    priceId: subscription.items.data[0]?.price.id,
  });

  // TODO: Update customer subscription status in database
  // TODO: Send subscription confirmation email
}

async function handleSubscriptionUpdated(subscription) {
  console.log('✓ Subscription updated:', {
    subscriptionId: subscription.id,
    status: subscription.status,
  });

  // TODO: Update subscription status in database
  if (subscription.status === 'past_due') {
    // TODO: Send payment retry reminder
  }
}

async function handleSubscriptionDeleted(subscription) {
  console.log('✓ Subscription cancelled:', {
    subscriptionId: subscription.id,
    customerId: subscription.customer,
  });

  // TODO: Deactivate account in database
  // TODO: Send cancellation confirmation email
}

async function handleInvoicePaymentSucceeded(invoice) {
  console.log('✓ Invoice paid:', {
    invoiceId: invoice.id,
    amount: invoice.amount_paid,
    customerId: invoice.customer,
  });

  // TODO: Log payment in database
}

async function handleInvoicePaymentFailed(invoice) {
  console.log('✗ Invoice payment failed:', {
    invoiceId: invoice.id,
    customerId: invoice.customer,
    attemptCount: invoice.attempt_count,
  });

  // TODO: Notify customer of failed payment
  // TODO: Trigger retry flow
}
