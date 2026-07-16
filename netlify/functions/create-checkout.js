/**
 * KaNun Monitoring — Stripe Checkout Creation
 * Netlify Function: /api/create-checkout
 * 
 * POST /api/create-checkout
 * Body: { priceId: "price_xxx", successUrl?: string, cancelUrl?: string }
 */

const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event, context) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };

  // Handle preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers };
  }

  // Only allow POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { priceId, successUrl, cancelUrl, customerEmail } = JSON.parse(event.body);

    // Validate required fields
    if (!priceId) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'priceId is required' }),
      };
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: successUrl || 'https://kanunmonitoring.com/billing-success?session_id={CHECKOUT_SESSION_ID}',
      cancel_url: cancelUrl || 'https://kanunmonitoring.com/billing-cancel',
      customer_email: customerEmail,
      subscription_data: {
        metadata: {
          order_id: `kanun-${Date.now()}`,
        },
      },
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        sessionId: session.id,
        url: session.url,
      }),
    };
  } catch (error) {
    console.error('Checkout error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: error.message || 'Failed to create checkout session',
      }),
    };
  }
};
