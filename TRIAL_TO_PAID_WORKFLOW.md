# KaNun Monitoring — Complete Stripe Workflow Documentation

## 🎯 CUSTOMER JOURNEY: From Free Trial to Paid Subscription

### **PHASE 1: DISCOVERY (Day 0)**

**What Happens:**
1. Customer visits: `https://lighthearted-brioche-b65f7d.netlify.app`
2. Scrolls to "Transparent Pricing" section
3. Clicks "Start 14-Day Free Trial" on desired tier
4. Redirected to Stripe Checkout

**Data Flow:**
```
Customer Click on Button
    ↓
stripe-checkout.js sends POST to /.netlify/functions/create-checkout
    ↓
create-checkout.js calls Stripe API with price ID
    ↓
Stripe returns checkout session
    ↓
Customer redirected to Stripe Checkout URL
    ↓
Customer enters email + payment method
```

**What Gets Created:**
- ✅ Stripe Customer object (if new)
- ✅ Stripe Subscription object (status: trialing)
- ✅ Invoice (with $0 charge during trial)

---

### **PHASE 2: TRIAL PERIOD (Days 1-13)**

**What Happens:**
1. Trial subscription is active
2. Customer can use full platform features
3. Stripe sends webhook: `customer.subscription.created`
4. Your backend should:
   - Create user account
   - Set `trial_ends_at` = 14 days from now
   - Store `stripe_customer_id` & `stripe_subscription_id`
   - Send welcome email

**Database Record Example:**
```json
{
  "user_id": "user_123",
  "email": "customer@example.com",
  "plan": "agency",
  "stripe_customer_id": "cus_xxxxx",
  "stripe_subscription_id": "sub_xxxxx",
  "trial_starts_at": "2026-07-14T00:00:00Z",
  "trial_ends_at": "2026-07-28T00:00:00Z",
  "status": "trialing",
  "created_at": "2026-07-14T00:00:00Z"
}
```

**Stripe Events During Trial:**
- `customer.subscription.created` — Sent immediately after checkout
- `invoice.created` (for $0) — Trial invoice logged

---

### **PHASE 3: TRIAL EXPIRATION MANAGEMENT (Days 10-14)**

**CRITICAL: This is where conversions happen!**

**Timeline:**
- **Day 10:** Send "Your trial expires in 4 days" email
- **Day 12:** Send "Last chance! 2 days left" reminder
- **Day 13:** Send urgent "Upgrade now or you'll lose access" message
- **Day 14:** Trial ends → Automatic charge or access revoked

**Recommended Email Sequence:**

```
Day 10 Email:
Subject: "Your KaNun trial expires in 4 days — here's what you need to know"
Body:
  - Recap of features they've used
  - Social proof ("100+ agencies use KaNun...")
  - Clear upgrade button
  - FAQ about billing

Day 12 Email:
Subject: "Last chance! 48 hours left for your free trial"
Body:
  - Urgency copy
  - "Upgrade now" CTA
  - Testimonial from similar agency
  - Money-back guarantee

Day 13 Email (Optional):
Subject: "Your KaNun trial ends tomorrow at midnight"
Body:
  - Final reminder
  - Direct upgrade link
  - Customer support contact info
```

---

### **PHASE 4: CONVERSION AT DAY 14**

**What Stripe Does Automatically:**
1. On Day 14, first real charge processes automatically
2. If payment succeeds → subscription continues
3. If payment fails → Stripe retries with escalating emails
4. If still fails → subscription cancelled

**What Your Backend Should Do:**

**Option A: Automatic Billing (Recommended)**
- Let Stripe charge automatically
- Respond to webhook: `invoice.payment_succeeded`
- Send confirmation email
- Update `status` to "active" in your database

**Option B: Manual Opt-in Before Day 14**
- Send upgrade flow email on Day 10
- Customer clicks link → goes through checkout again
- Subscription converts immediately
- Less automatic billing, more engagement

**Webhook Flow at Day 14:**
```
Day 14 at 00:00 UTC
    ↓
Stripe generates invoice for next month
    ↓
Stripe attempts to charge stored payment method
    ↓
Payment succeeds
    ↓
Webhook: invoice.payment_succeeded
    ↓
Your backend should:
  - Update database: status = "active"
  - Send receipt email
  - Log payment in audit trail
```

---

### **PHASE 5: ACTIVE SUBSCRIPTION (Day 15+)**

**What Happens:**
- Customer now in active subscription
- Monthly recurring charges
- Full access to platform
- Subscription continues until cancelled

**Regular Webhooks:**
- `invoice.payment_succeeded` — Monthly on billing date
- `invoice.payment_failed` — If card declines
- `customer.subscription.updated` — If they change plans
- `customer.subscription.deleted` — If they cancel

---

## 🧪 TESTING THE WORKFLOW WITH munya@kanunmonitoring.com

### **Step 1: Use Stripe Test Mode**

First, switch Stripe Dashboard to TEST mode:
```
1. Go to https://dashboard.stripe.com
2. Top-left corner: Toggle "Viewing test data"
3. This switches to test keys (starts with sk_test_)
```

### **Step 2: Reset Website to Test Mode**

Update Netlify environment variables:
```bash
netlify env:set STRIPE_SECRET_KEY sk_test_<YOUR_TEST_SECRET_KEY>
netlify deploy --prod
```

Get your test secret key from: https://dashboard.stripe.com/test/apikeys

### **Step 3: Test Checkout with munya@kanunmonitoring.com**

**Complete Workflow Test:**

1. **Visit the site:**
   ```
   https://lighthearted-brioche-b65f7d.netlify.app
   ```

2. **Click "Start 14-Day Free Trial" on Agency plan** ($79/month)
   - This is a good middle-tier plan for testing

3. **At Stripe Checkout, enter:**
   ```
   Email: munya@kanunmonitoring.com
   Card:  4242 4242 4242 4242
   Exp:   12/25
   CVC:   123
   Zip:   12345
   ```

4. **Complete the form and submit**

5. **What You'll See:**
   - ✅ Payment processes instantly
   - ✅ Redirected to `/billing-success` page
   - ✅ Webhook fires automatically

### **Step 4: Verify in Stripe Dashboard**

Go to https://dashboard.stripe.com/test/customers and look for:
- ✅ New customer with email `munya@kanunmonitoring.com`
- ✅ Active subscription (status: "trialing")
- ✅ Trial period: 14 days
- ✅ Next charge date: 14 days from now

### **Step 5: Check Webhook Logs**

In Netlify Dashboard:
```
1. Go to: Functions > Logs
2. Find: webhooks-stripe function
3. You should see these events:
   ✅ checkout.session.completed
   ✅ customer.subscription.created
   ✅ invoice.created
```

### **Step 6: Simulate Trial Expiration**

In Stripe test dashboard:
1. Go to: https://dashboard.stripe.com/test/subscriptions
2. Find subscription for munya@kanunmonitoring.com
3. Click the subscription ID
4. Click "..." (three dots)
5. Select "Mark subscription as past due" or force payment with:
   ```
   curl -X POST https://api.stripe.com/v1/test_helpers/test_clocks/attach \
     -u sk_test_YOUR_KEY: \
     -d "subscription=sub_xxxxx" \
     -d "frozen_time=1726320000"
   ```

---

## ⏰ TRIAL-TO-PAID CONVERSION SYSTEM

### **What You Need to Build (in your backend)**

**1. Trial Expiration Job (runs daily)**

```python
# Daily cron job at 1 AM UTC
def check_expiring_trials():
    # Get all subscriptions expiring in 4 days
    expiring_soon = Subscription.filter(
        trial_ends_at__gte=tomorrow,
        trial_ends_at__lt=in_4_days,
        status="trialing",
        email_sent_day_10=False
    )
    
    for sub in expiring_soon:
        send_email(
            to=sub.customer_email,
            template="trial_expiring_4_days",
            data={
                "days_left": 4,
                "plan_name": sub.plan,
                "plan_price": sub.plan_price,
                "feature_count": count_used_features(sub.customer_id),
                "signup_link": generate_upgrade_link(sub.stripe_subscription_id)
            }
        )
        sub.email_sent_day_10 = True
        sub.save()
```

**2. Webhook Handler for Trial Ending**

```python
# In webhooks-stripe.js handler
async function handleInvoiceCreatedForTrial(invoice) {
    // When invoice is created at day 14
    if (invoice.subscription && invoice.lines.data[0]?.period.start) {
        const sub = await stripe.subscriptions.retrieve(invoice.subscription);
        
        if (sub.status === 'trialing') {
            // Still in trial - this is the day 14 renewal
            // Send final reminder: "Payment processing tomorrow"
            await sendEmail({
                to: invoice.customer_email,
                template: 'trial_ending_tomorrow',
                data: { 
                    trial_ends_at: sub.trial_end,
                    plan_name: sub.items.data[0].price.product.name
                }
            });
        }
    }
}

async function handleInvoicePaymentSucceeded(invoice) {
    // Successful charge at day 14+
    const sub = await stripe.subscriptions.retrieve(invoice.subscription);
    
    // Update database
    await Subscription.update({
        stripe_subscription_id: sub.id
    }, {
        status: 'active',
        trial_ends_at: null,
        last_invoice_date: new Date(),
        next_invoice_date: sub.current_period_end
    });
    
    // Send receipt & welcome email
    await sendEmail({
        to: invoice.customer_email,
        template: 'welcome_active_subscription',
        data: {
            plan_name: sub.items.data[0].price.product.name,
            amount_charged: invoice.amount_paid / 100,
            next_billing_date: new Date(sub.current_period_end * 1000)
        }
    });
}
```

**3. Database Schema**

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    stripe_customer_id VARCHAR NOT NULL,
    stripe_subscription_id VARCHAR NOT NULL,
    customer_email VARCHAR NOT NULL,
    plan VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'trialing', -- trialing, active, past_due, cancelled
    
    trial_starts_at TIMESTAMP,
    trial_ends_at TIMESTAMP,
    
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    next_invoice_date TIMESTAMP,
    last_invoice_date TIMESTAMP,
    
    email_sent_day_10 BOOLEAN DEFAULT FALSE,
    email_sent_day_12 BOOLEAN DEFAULT FALSE,
    email_sent_day_13 BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(stripe_subscription_id)
);
```

---

## 📊 TESTING CHECKLIST

### **Test Case 1: Successful Trial → Paid Conversion**

- [ ] Click "Start Trial" on home page
- [ ] Use test card `4242 4242 4242 4242`
- [ ] Email: `munya@kanunmonitoring.com`
- [ ] See `/billing-success` page
- [ ] Verify Stripe customer created in dashboard
- [ ] Verify subscription status = "trialing"
- [ ] Check webhook logs show `subscription.created`
- [ ] Wait 14 days (or simulate with Stripe test clock)
- [ ] Verify automatic charge processes
- [ ] Verify `invoice.payment_succeeded` webhook fires

### **Test Case 2: Failed Payment on Day 14**

- [ ] Use card: `4000 0000 0000 0002` (decline)
- [ ] Complete trial
- [ ] On day 14, payment fails
- [ ] Verify `invoice.payment_failed` webhook fires
- [ ] Verify retry logic kicks in
- [ ] Check customer receives payment failure email

### **Test Case 3: Manual Cancellation**

- [ ] Create trial subscription
- [ ] Go to Stripe dashboard > Subscriptions
- [ ] Cancel the subscription
- [ ] Verify `customer.subscription.deleted` webhook fires
- [ ] Verify user loses access in your app

### **Test Case 4: Trial → Active Email Sequence**

- [ ] Create subscription
- [ ] Trigger day 10 email job
- [ ] Verify "expires in 4 days" email sent
- [ ] Trigger day 12 email
- [ ] Verify "last chance" email sent
- [ ] At day 14, payment processes
- [ ] Verify welcome email sent

---

## 🎯 LIVE ENVIRONMENT: PRODUCTION PAYOUTS

Once you switch from test to LIVE:

1. **Update Netlify to use LIVE key:**
   ```bash
   netlify env:set STRIPE_SECRET_KEY sk_live_YOUR_LIVE_KEY
   netlify deploy --prod
   ```

2. **Real payments will start:**
   - Customers actually charged
   - Money goes to your Stripe account
   - Payouts to your bank account

3. **Update Stripe webhook URL:**
   - Go to: https://dashboard.stripe.com/webhooks
   - Edit the webhook endpoint
   - Change URL to use your custom domain
   - Keep signing secret the same

---

## 📞 EMAIL TEMPLATES YOU SHOULD CREATE

### **Template 1: Welcome Email (Day 0, after payment)**
```
Subject: Welcome to KaNun Monitoring! Your 14-day trial has started

Hi [Customer Name],

Your trial subscription is now active! Here's what you can do:

✓ [Feature 1]
✓ [Feature 2]
✓ [Feature 3]

Your trial ends: [DATE]

Questions? Reply to this email or visit our help center.

Best regards,
KaNun Monitoring Team
```

### **Template 2: Trial Expiring Soon (Day 10)**
```
Subject: Your KaNun trial expires in 4 days

Hi [Customer Name],

We noticed you've been using [X features] in KaNun. Here's what you've accomplished:

[Show their usage: X visits scheduled, X reports generated, etc.]

Your trial expires in 4 days: [DATE]

After your trial, your account will automatically convert to your chosen plan:
[Plan Name] - $[Price]/month

To manage your subscription: [Link]
Questions? [Support link]
```

### **Template 3: Last Chance (Day 13)**
```
Subject: Last chance! Your trial ends tomorrow

Hi [Customer Name],

⚠️ Your KaNun trial ends TOMORROW at midnight.

At that time, we'll charge your card for [Plan Name]:
[Price] / month

To change plans or cancel: [Link]
```

### **Template 4: Welcome to Active Subscription (Day 14+)**
```
Subject: Your subscription is now active!

Hi [Customer Name],

Great news! Your payment went through successfully.

Subscription Details:
- Plan: [Plan Name]
- Amount: $[Price]/month
- Next Billing: [DATE]

Your account now has full access to:
✓ [All features for your plan]

Need help? [Support link]
```

---

## 🔄 THE COMPLETE FLOW AT A GLANCE

```
Day 0: Customer clicks "Start Trial"
       ↓
     Stripe Checkout
       ↓
     Email: munya@kanunmonitoring.com
     Payment Method: Saved
     Status: trialing
       ↓
Day 0: Welcome Email
       ↓
Days 1-9: Customer uses platform freely
       ↓
Day 10: "Trial expires in 4 days" email
       ↓
Days 11-13: Continue using
       ↓
Day 12: "Last chance" email
       ↓
Day 13: "Expires tomorrow" email
       ↓
Day 14 at 00:00 UTC:
  - Stripe generates invoice
  - Charges saved card automatically
  - If successful → status = "active"
  - If failed → status = "past_due" (retry for 3 days)
       ↓
Day 14+: Confirmation email sent
       ↓
Monthly: Recurring charge on billing date
       ↓
Future: If they cancel → status = "cancelled"
```

---

## 💡 CONVERSION OPTIMIZATION TIPS

1. **Show value early:** Let users see data/reports within first 2 days
2. **Send Day 10 email with stats:** "You've saved 6 hours with KaNun"
3. **Use urgency:** "Only 48 hours left" is more effective than "4 days left"
4. **Offer discount:** Consider offering 10% off annual plans on day 12
5. **Include testimonial:** "60 other agencies trust KaNun..."
6. **Make cancellation easy:** But ask "Why are you cancelling?" → shows retention data
7. **Follow up after cancellation:** "We miss you - come back for 20% off"

---

## 🚀 NEXT STEPS

1. **Set up your backend** to handle webhooks from `webhooks-stripe.js`
2. **Create email templates** for the 4 critical moments
3. **Add database schema** to track subscriptions & trial status
4. **Build trial expiration job** that runs daily
5. **Test with munya@kanunmonitoring.com** using Stripe test mode
6. **Monitor metrics:** Conversion rate, churn rate, customer lifetime value
