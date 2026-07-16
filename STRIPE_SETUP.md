# KaNun Monitoring — Stripe Subscription Setup Guide

## ✅ Completed Steps

### Step 1: Create Products ✓
Products created for all 3 subscription tiers:
- **Solo Monitor** — $39/month
- **Agency** — $79/month  
- **Agency Pro** — $149/month (Popular)

### Step 2: Success & Cancel Pages ✓
Created and deployed:
- `/billing-success.html` — Confirmation page with next steps
- `/billing-cancel.html` — Cancellation page with retry offer

### Step 3: Stripe Configuration Files ✓
- `stripe_setup.py` — Product & price creation script
- `stripe_webhook_handler.py` — Event processing for subscriptions

---

## 🔧 Implementation Steps

### Step 1: Set Your Stripe API Key

```bash
# Export your Stripe SECRET key
export STRIPE_SECRET_KEY='sk_live_YOUR_LIVE_KEY_HERE'

# Or for testing:
export STRIPE_SECRET_KEY='sk_test_YOUR_TEST_KEY_HERE'
```

### Step 2: Run the Setup Script

```bash
cd /Users/geoffrey/kanun-monitoring-next

# Create all products and prices (generates stripe_config_live.json)
python3 stripe_setup.py --live

# Or test mode:
python3 stripe_setup.py
```

**Output will contain:**
```json
{
  "stripe_mode": "live",
  "products": {
    "solo_monitor": {
      "product_id": "prod_XXXXX",
      "name": "Solo Monitor"
    },
    "agency": {
      "product_id": "prod_YYYYY",
      "name": "Agency"
    },
    "agency_pro": {
      "product_id": "prod_ZZZZZ",
      "name": "Agency Pro"
    }
  },
  "prices": {
    "solo_monitor": {
      "price_id": "price_xxxxx",
      "amount": 3900,
      "currency": "usd"
    },
    ...
  }
}
```

### Step 3: Create Checkout Button (HTML/JavaScript)

```html
<!-- Add to your pricing page or signup flow -->
<button id="checkout-btn" data-price-id="price_xxxxx">
  Start Free Trial
</button>

<script src="https://js.stripe.com/v3/"></script>
<script>
  const stripe = Stripe('pk_live_YOUR_PUBLISHABLE_KEY');
  
  document.getElementById('checkout-btn').addEventListener('click', async (e) => {
    const priceId = e.target.getAttribute('data-price-id');
    
    // Create checkout session on your backend
    const response = await fetch('/api/create-checkout-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ price_id: priceId })
    });
    
    const session = await response.json();
    
    // Redirect to Stripe Checkout
    await stripe.redirectToCheckout({ sessionId: session.id });
  });
</script>
```

### Step 4: Create Checkout Session Endpoint (Backend)

**Python (FastAPI):**
```python
from fastapi import FastAPI
import stripe

app = FastAPI()

@app.post('/api/create-checkout-session')
async def create_checkout_session(data: dict):
    """Create a Stripe checkout session"""
    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            success_url='https://kanunmonitoring.com/billing-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://kanunmonitoring.com/billing-cancel',
            line_items=[
                {
                    'price': data['price_id'],
                    'quantity': 1,
                },
            ],
        )
        
        return {
            'id': session.id,
            'url': session.url,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Node.js (Express):**
```javascript
const express = require('express');
const app = express();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

app.post('/api/create-checkout-session', async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      success_url: 'https://kanunmonitoring.com/billing-success?session_id={CHECKOUT_SESSION_ID}',
      cancel_url: 'https://kanunmonitoring.com/billing-cancel',
      line_items: [
        {
          price: req.body.price_id,
          quantity: 1,
        },
      ],
    });

    res.json({ id: session.id, url: session.url });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

### Step 5: Deploy Success & Cancel Pages to Netlify

```bash
cd /Users/geoffrey/kanun-monitoring-next

# Deploy (your existing Netlify setup)
netlify deploy --prod

# Verify URLs are live:
curl https://kanunmonitoring.com/billing-success
curl https://kanunmonitoring.com/billing-cancel
```

### Step 6: Set Up Webhooks

**In Stripe Dashboard:**
1. Go to **Developers > Webhooks**
2. Click **Add an endpoint**
3. Enter: `https://api.kanunmonitoring.com/webhooks/stripe`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook secret (starts with `whsec_`)

**In your .env file:**
```bash
STRIPE_WEBHOOK_SECRET='whsec_YOUR_SECRET_HERE'
```

**Add webhook handler to your backend:**

```python
# FastAPI example
from fastapi import Request
from stripe_webhook_handler import webhook_handler

@app.post('/webhooks/stripe')
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get('stripe-signature')
    result, status_code = webhook_handler(body.decode(), signature)
    return result
```

### Step 7: Test the Flow Locally

```bash
# Start Stripe CLI webhook listener
stripe listen --forward-to localhost:8000/webhooks/stripe

# Use test card: 4242 4242 4242 4242
# Expiry: Any future date (12/25)
# CVC: Any 3 digits (123)

# Watch for webhook events in your terminal
```

---

## 📋 Pricing & Trial Details

| Tier | Price | Trial | Features |
|------|-------|-------|----------|
| **Solo Monitor** | $39/month | 14 days | Mobile platform, client intake, GPS docs, reports, email auto-filing |
| **Agency** | $79/month | 14 days | Everything in Solo + up to 5 monitors, agency dashboard, team scheduling |
| **Agency Pro** | $149/month | 14 days | Everything in Agency + unlimited monitors, advanced analytics, priority support, custom branding |
| **KCM Certification** | $499 initial<br>$149/year renewal | N/A | Optional credential (standalone) |

---

## 🎯 Next Steps Checklist

- [ ] Set `STRIPE_SECRET_KEY` environment variable
- [ ] Run `python3 stripe_setup.py --live` to create products
- [ ] Save the generated `stripe_config_live.json`
- [ ] Deploy success/cancel pages to Netlify
- [ ] Build checkout button & create-session endpoint
- [ ] Set up webhook endpoint in Stripe Dashboard
- [ ] Set `STRIPE_WEBHOOK_SECRET` in `.env`
- [ ] Deploy webhook handler to backend
- [ ] Test with Stripe CLI in local environment
- [ ] Test checkout flow end-to-end with test card
- [ ] Go live! 🚀

---

## 📚 Resources

- **Stripe Docs:** https://stripe.com/docs/billing/subscriptions/checkout
- **Webhook Events:** https://stripe.com/docs/api/events/types
- **Test Cards:** https://stripe.com/docs/testing
- **Stripe CLI:** https://stripe.com/docs/stripe-cli

---

## Support

Questions? Contact Munya at munya@kanunmonitoring.com
