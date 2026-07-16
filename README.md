# KaNun Monitoring — Stripe Live Subscription Platform

Production platform for supervised visitation with integrated Stripe payment processing for SaaS subscriptions.

**Live:** https://kanunmonitoring.com

## 📊 Project Overview

KaNun Monitoring is a professional platform for supervised visitation scheduling, documentation, and court-ready reporting. This repository contains the complete Stripe Live integration for subscription billing.

### Features

- ✅ **3 Subscription Tiers:** Solo Monitor ($39/mo), Agency ($79/mo), Agency Pro ($149/mo)
- ✅ **14-Day Free Trial:** All plans include trial period with full feature access
- ✅ **Stripe Live Integration:** Production payment processing
- ✅ **Netlify Functions:** Serverless checkout & webhook handlers
- ✅ **Automatic Billing:** Recurring charges after trial period
- ✅ **Webhook Management:** 6 event types (checkout, subscription, invoice)
- ✅ **Email Workflow:** Trial expiration reminders & conversion emails

## 🚀 Live Deployment Status

| Component | Status | Location |
|-----------|--------|----------|
| **Website** | ✅ Live | https://kanunmonitoring.com |
| **Checkout** | ✅ Live | Stripe Hosted Checkout |
| **Webhooks** | ✅ Active | `/.netlify/functions/webhooks-stripe` |
| **Stripe Mode** | ✅ Live | Production (sk_live_*) |
| **Domain** | ✅ Connected | Netlify custom domain |

---

## 📁 Directory Structure

```
kanun-monitoring-next/
├── index.html                          # Home page with pricing
├── signup.html                         # Sign-up page
├── login.html                          # Login page
├── billing-success.html                # Post-checkout success page
├── billing-cancel.html                 # Checkout cancellation page
│
├── netlify/
│   └── functions/
│       ├── create-checkout.js          # POST endpoint to create Stripe sessions
│       └── webhooks-stripe.js          # Webhook handler for Stripe events
│
├── stripe-checkout.js                  # Frontend button handler
├── stripe_config_live.json             # Product & price IDs
├── stripe_setup.py                     # One-time setup script (already run)
├── stripe_webhook_handler.py           # Python webhook reference implementation
│
├── netlify.toml                        # Netlify configuration
├── package.json                        # Dependencies (stripe lib)
├── .env.example                        # Environment variables template
│
└── docs/
    ├── TRIAL_TO_PAID_WORKFLOW.md       # Complete customer journey
    ├── STRIPE_ALL_TASKS_COMPLETE.md    # Setup completion summary
    ├── STRIPE_FINAL_STATUS.md          # Technical details
    └── STRIPE_COMPLETE_SETUP.md        # Step-by-step guide
```

---

## 🔑 Configuration

### Environment Variables (Netlify)

These are set in Netlify Dashboard > Site Settings > Build & Deploy > Environment

```
STRIPE_SECRET_KEY=sk_live_51Tq7o4Bryn2IZeeR...
STRIPE_WEBHOOK_SECRET=whsec_USZ6tyvSpq61F3bQIpsO0boq8iWzKPaq
```

**⚠️ SECURITY:** Never commit `.env` files or expose secret keys in the codebase.

---

## 💰 Stripe Configuration

### Products

| Product | Price | Trial | Product ID |
|---------|-------|-------|-----------|
| Solo Monitor | $39/month | 14 days | prod_Ut1fokU6Qc1YlL |
| Agency | $79/month | 14 days | prod_Ut1fnuhAjMZzQf |
| Agency Pro | $149/month | 14 days | prod_Ut1fqFcQDZXKC0 |

### Prices

| Plan | Price ID | Amount | Billing |
|------|----------|--------|---------|
| Solo Monitor | price_1TtFcKBryn2IZeeRuZhZJJJL | $39 | Monthly |
| Agency | price_1TtFcKBryn2IZeeRwxvZ0Swh | $79 | Monthly |
| Agency Pro | price_1TtFcLBryn2IZeeRXlzKL5LI | $149 | Monthly |

### Webhook Configuration

| Setting | Value |
|---------|-------|
| Endpoint ID | we_1TtHiLBryn2IZeeR8YjmcW3G |
| URL | https://kanunmonitoring.com/.netlify/functions/webhooks-stripe |
| Signing Secret | whsec_USZ6tyvSpq61F3bQIpsO0boq8iWzKPaq |
| Status | ✅ Enabled |

**Events Configured:**
- `checkout.session.completed` — Successful checkout
- `customer.subscription.created` — New subscription (trial start)
- `customer.subscription.updated` — Plan change
- `customer.subscription.deleted` — Cancellation
- `invoice.payment_succeeded` — Recurring charge success
- `invoice.payment_failed` — Payment declined

---

## 🧪 Testing

### Test with Production Site

1. **Visit:** https://kanunmonitoring.com
2. **Scroll to:** "Transparent Pricing" section
3. **Click:** "Start 14-Day Free Trial" on any tier
4. **Complete Stripe Checkout** with:
   - Email: your email
   - Card: `4242 4242 4242 4242` (test card that always succeeds in live mode for testing purposes)
   - Exp: `12/25`
   - CVC: `123`
5. **Verify:** Redirected to `/billing-success` page
6. **Check Webhook Logs:** 
   - Netlify Dashboard > Functions > webhooks-stripe
   - Should see `checkout.session.completed` event

### Test Webhook Reception

```bash
# Test webhook endpoint
curl -X POST https://kanunmonitoring.com/.netlify/functions/webhooks-stripe \
  -H "Content-Type: application/json" \
  -d '{"type": "ping"}'
```

### Monitoring

**Stripe Dashboard:**
- View subscriptions: https://dashboard.stripe.com/subscriptions
- View customers: https://dashboard.stripe.com/customers
- View webhooks: https://dashboard.stripe.com/webhooks

**Netlify Dashboard:**
- Function logs: https://app.netlify.com/sites/lighthearted-brioche-b65f7d/functions
- Deploy logs: https://app.netlify.com/sites/lighthearted-brioche-b65f7d/deploys

---

## 📋 Checkout Flow (Customer Perspective)

```
1. Visit https://kanunmonitoring.com
   ↓
2. See pricing section with 3 tiers
   ↓
3. Click "Start 14-Day Free Trial"
   ↓
4. Redirected to Stripe Hosted Checkout
   ↓
5. Enter email + payment method
   ↓
6. Click "Subscribe"
   ↓
7. Redirected to /billing-success
   ↓
8. Webhook events fire:
   - checkout.session.completed
   - customer.subscription.created
   - invoice.created (for $0 trial charge)
```

---

## 🔄 Trial-to-Paid Workflow

### Timeline

| Day | Action | Email |
|-----|--------|-------|
| 0 | Trial starts after checkout | Welcome |
| 10 | System should send reminder | "4 days left" |
| 12 | System should send urgency | "48 hours left" |
| 13 | System should send final reminder | "Expires tomorrow" |
| 14 | Automatic charge processes | Confirmation |
| 15+ | Active subscription | Regular billing |

### What Happens at Day 14

1. **Stripe generates invoice** for next billing period
2. **Charges saved payment method** automatically
3. **If successful:**
   - Webhook: `invoice.payment_succeeded`
   - Subscription status: `active`
   - Send confirmation email
4. **If failed:**
   - Webhook: `invoice.payment_failed`
   - Subscription status: `past_due`
   - Stripe retries for 3 days
   - Send payment failure email

### Webhook Events During Trial

```
checkout.session.completed    → User completes checkout
customer.subscription.created → Trial subscription created
invoice.created (for $0)      → Trial invoice logged
```

### Webhook Events at Day 14

```
invoice.created              → Invoice generated for first real charge
invoice.payment_attempted    → Payment attempt made
invoice.payment_succeeded    → Payment successful (or failed)
```

**Your backend should:**
- Create user account on `subscription.created`
- Set `trial_ends_at = 14 days from now`
- Update status to `active` on `invoice.payment_succeeded`
- Send transactional emails for each event

---

## 🔌 API Endpoints

### Create Checkout Session

**POST** `/.netlify/functions/create-checkout`

```bash
curl -X POST https://kanunmonitoring.com/.netlify/functions/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "priceId": "price_1TtFcKBryn2IZeeRuZhZJJJL",
    "customerEmail": "user@example.com",
    "successUrl": "https://kanunmonitoring.com/billing-success",
    "cancelUrl": "https://kanunmonitoring.com/billing-cancel"
  }'
```

**Response:**
```json
{
  "sessionId": "cs_live_a1VR13xyvr6WgwA0YVbKQs...",
  "checkoutUrl": "https://checkout.stripe.com/pay/cs_live_..."
}
```

### Webhook Endpoint

**POST** `/.netlify/functions/webhooks-stripe`

Listens for Stripe events. Requires `Stripe-Signature` header for verification.

```bash
# Stripe sends this automatically
curl -X POST https://kanunmonitoring.com/.netlify/functions/webhooks-stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=1...,v1=..." \
  -d '{
    "id": "evt_1...",
    "type": "checkout.session.completed",
    "data": {...}
  }'
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **TRIAL_TO_PAID_WORKFLOW.md** | Complete customer journey, testing guide, email templates |
| **STRIPE_ALL_TASKS_COMPLETE.md** | Setup completion summary & verification |
| **STRIPE_FINAL_STATUS.md** | Technical status & configuration details |
| **STRIPE_COMPLETE_SETUP.md** | Step-by-step implementation guide |

---

## 🛠 Development Setup

### Prerequisites

- Node.js 16+
- npm or yarn
- Netlify CLI
- GitHub account

### Local Development

```bash
# Clone repo
git clone https://github.com/kanunwell/kanun-monitoring-next.git
cd kanun-monitoring-next

# Install dependencies
npm install

# Set environment variables (ask team)
export STRIPE_SECRET_KEY=sk_live_...
export STRIPE_WEBHOOK_SECRET=whsec_...

# Deploy locally (Netlify Dev)
netlify dev

# Site available at: http://localhost:8888
```

### Deploy to Production

```bash
# Changes are auto-deployed when pushed to main
# Manual deploy if needed:
netlify deploy --prod
```

---

## 🚨 Important Notes

### Security

- ✅ Secret keys stored in Netlify environment (not in repo)
- ✅ Webhook signature verification enabled
- ✅ API keys never logged or exposed
- ✅ HTTPS enforced (Netlify default)

### Trial Management

**⚠️ Important:** The trial-to-paid conversion emails are NOT yet automated. You need to:

1. **Build a backend service** that:
   - Stores subscription data from webhooks
   - Runs daily job to check expiring trials
   - Sends reminder emails on days 10, 12, 13
   - Logs conversion metrics

2. **Listen to these webhooks:**
   - `customer.subscription.created` — New subscription (save trial end date)
   - `invoice.payment_succeeded` — Charge succeeded (update status)
   - `invoice.payment_failed` — Charge failed (send retry email)

3. **See:** `TRIAL_TO_PAID_WORKFLOW.md` for full implementation guide

### Stripe Account

- **Mode:** Live (production)
- **Account:** acct_1Tq7o4Bryn2IZeeR
- **Payouts:** To connected bank account
- **Disputes:** Handled via Stripe Dashboard

---

## 📞 Support

For issues or questions:

1. Check **Stripe Dashboard** for transaction/webhook logs
2. Check **Netlify Dashboard** for function execution logs
3. Review **documentation files** in `/docs` directory
4. Contact Stripe support: support@stripe.com

---

## 📝 Changelog

### v1.0.0 — 2026-07-14

- ✅ Initial Stripe Live integration
- ✅ 3 pricing tiers with products & prices created
- ✅ Netlify Functions deployed (checkout & webhooks)
- ✅ Pricing page with checkout buttons
- ✅ Billing success/cancel pages
- ✅ Webhook configuration in Stripe
- ✅ Complete documentation

---

## 📄 License

Internal use only. Kanun Monitoring proprietary.
