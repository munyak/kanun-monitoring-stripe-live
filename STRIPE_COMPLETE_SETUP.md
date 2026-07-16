# KaNun Monitoring — Stripe Checkout Complete Setup

## ✅ STEP 1: Deploy Billing Pages to Netlify

**Status:** READY TO DEPLOY
- `billing-success.html` — Customer confirmation page
- `billing-cancel.html` — Retry offer page
- Both files are already in `/kanun-monitoring-next/`

### Deploy Command:
```bash
cd /Users/geoffrey/kanun-monitoring-next
netlify deploy --prod
```

---

## ✅ STEP 2: Netlify Functions Created

**Checkout Endpoint:** `/.netlify/functions/create-checkout`
- Creates Stripe checkout sessions
- Input: `{ priceId, customerEmail, successUrl?, cancelUrl? }`
- Output: `{ sessionId, url }`

**Webhook Handler:** `/.netlify/functions/webhooks-stripe`
- Listens for Stripe events
- Handles subscriptions, payments, invoices
- Ready for custom business logic

### Files Created:
```
netlify/functions/
├── create-checkout.js        (Checkout session creation)
└── webhooks-stripe.js        (Webhook event processing)
```

### Required Environment Variables (Set in Netlify Dashboard):
```
STRIPE_SECRET_KEY=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
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxx (generated after webhook setup)
```

---

## ✅ STEP 3: Configure Webhook in Stripe Dashboard

### Instructions:

1. **Go to Stripe Dashboard**
   - URL: https://dashboard.stripe.com/
   - Navigate to: Developers > Webhooks

2. **Create New Endpoint**
   - Endpoint URL: `https://kanunmonitoring.com/.netlify/functions/webhooks-stripe`
   - (After deploying to Netlify)

3. **Select Events to Listen For**
   Check these boxes:
   - ✅ checkout.session.completed
   - ✅ customer.subscription.created
   - ✅ customer.subscription.updated
   - ✅ customer.subscription.deleted
   - ✅ invoice.payment_succeeded
   - ✅ invoice.payment_failed

4. **Copy Signing Secret**
   - After creating, you'll see: "Signing secret: whsec_..."
   - Copy this value

5. **Set Environment Variable**
   - Go to Netlify Dashboard > Site Settings > Build & Deploy > Environment
   - Add: `STRIPE_WEBHOOK_SECRET=whsec_xxxxx`
   - Redeploy site

---

## ✅ STEP 4: Test Checkout Flow End-to-End

### Test Setup (WITHOUT REAL CHARGES):

1. **Use Stripe Test Mode**
   - Go to Stripe Dashboard
   - Toggle "Viewing test data" (top-left corner)
   - Use test secret key: `sk_test_51Tq7o4Bryn2IZeeR...` (starts with sk_test)

2. **Test Card Numbers** (will not be charged):
   ```
   Visa:          4242 4242 4242 4242
   Visa (Decline): 4000 0000 0000 0002
   Amex:          3782 822463 10005
   
   Exp: Any future date (e.g., 12/25)
   CVC: Any 3 digits (e.g., 123)
   Zip: Any 5 digits (e.g., 12345)
   ```

3. **Add Checkout Button to Your Site**
   
   Add to `index.html` or any page where you want to sell:
   ```html
   <!-- Price IDs from stripe_config_live.json -->
   <div class="pricing">
     <button class="checkout-btn" data-price-id="price_1TtFcKBryn2IZeeRuZhZJJJL">
       Subscribe to Solo Monitor - $39/month
     </button>
     
     <button class="checkout-btn" data-price-id="price_1TtFcKBryn2IZeeRwxvZ0Swh">
       Subscribe to Agency - $79/month
     </button>
     
     <button class="checkout-btn" data-price-id="price_1TtFcLBryn2IZeeRXlzKL5LI">
       Subscribe to Agency Pro - $149/month
     </button>
   </div>

   <!-- Load our Stripe handler -->
   <script src="stripe-checkout.js"></script>
   ```

4. **Test the Flow**
   ```
   a) User clicks "Subscribe" button
   b) Page calls /.netlify/functions/create-checkout
   c) Redirects to Stripe Checkout
   d) User enters test card: 4242 4242 4242 4242
   e) Completes payment
   f) Redirected to /billing-success
   g) Webhook fires automatically (Stripe → Netlify function)
   h) Check logs: Netlify Functions > webhooks-stripe
   ```

5. **Verify in Stripe Dashboard**
   - Customers: See test customer created
   - Subscriptions: See test subscription active
   - Invoices: See test invoice paid

---

## PRICE IDS (from stripe_config_live.json)

| Tier | Price ID | Monthly Cost |
|------|----------|--------------|
| Solo Monitor | price_1TtFcKBryn2IZeeRuZhZJJJL | $39 |
| Agency | price_1TtFcKBryn2IZeeRwxvZ0Swh | $79 |
| Agency Pro | price_1TtFcLBryn2IZeeRXlzKL5LI | $149 |

---

## DEPLOYMENT CHECKLIST

- [ ] Deploy to Netlify: `netlify deploy --prod`
- [ ] Verify pages live: https://kanunmonitoring.com/billing-success
- [ ] Verify endpoints live: Call `/.netlify/functions/create-checkout` (should return 400 with "priceId is required")
- [ ] Add checkout buttons to your site (use HTML above)
- [ ] Create Stripe webhook endpoint
- [ ] Set `STRIPE_WEBHOOK_SECRET` env var in Netlify
- [ ] Test with Stripe test card
- [ ] Verify webhook logs in Netlify Functions
- [ ] Verify test subscription in Stripe Dashboard
- [ ] Switch to LIVE mode when ready (use live secret key)

---

## NEXT: INTEGRATE WITH YOUR APP

The webhook handler has TODO placeholders for:
- Save customers to database
- Send welcome emails
- Activate/deactivate accounts
- Log payments
- Handle payment failures

Edit `/netlify/functions/webhooks-stripe.js` and fill in the TODOs with your business logic.

---

## SUPPORT LINKS

- [Stripe Webhook Events](https://stripe.com/docs/api/events)
- [Checkout Session API](https://stripe.com/docs/api/checkout/sessions/create)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)
- [Stripe Dashboard](https://dashboard.stripe.com/)
