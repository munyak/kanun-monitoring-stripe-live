# 🧪 PRODUCTION TESTING GUIDE — KaNun Monitoring Stripe Live

**Site:** https://kanunmonitoring.com  
**Stripe Mode:** LIVE (Real money processing)  
**Status:** ✅ Ready for testing & customer acquisition

---

## ⚠️ IMPORTANT BEFORE YOU TEST

**LIVE MODE WARNING:**
- This site processes REAL payments
- Test transactions will be charged to your Stripe account
- Do NOT use random email addresses — use your own for accountability
- Each test creates a real customer record in Stripe

**Test Email:** `munya@kanunmonitoring.com`

---

## 🧪 STEP-BY-STEP TESTING GUIDE

### Step 1: Verify Site is Live

```
Open: https://kanunmonitoring.com
Expected:
  ✅ Home page loads
  ✅ Pricing section visible at bottom
  ✅ 3 pricing cards (Solo, Agency, Agency Pro)
  ✅ Each has "Start 14-Day Free Trial" button
  ✅ Footer shows: "Professional supervised visitation management"
```

### Step 2: Test Checkout on Solo Monitor Tier

**Action:**
1. Scroll to "Pricing" section
2. Click "Start 14-Day Free Trial" on **Solo Monitor** ($39/month)
3. You should be redirected to Stripe Checkout

**Expected at Stripe Checkout:**
```
- Price: $39.00 USD
- Trial period: 14 days
- Auto-renews after trial
- Payment method field (card)
- Email field pre-filled (possibly)
```

**Enter Payment Details:**
```
Email:    munya@kanunmonitoring.com
Card:     4242 4242 4242 4242  (always succeeds in live)
Exp:      12/25
CVC:      123
Zip:      12345
```

**Note:** This is a REAL charge to test Stripe Live with actual processing. Use a card you want to test with.

### Step 3: Verify Checkout Success

**Expected After Submission:**
```
✅ Stripe processes payment
✅ Page redirects to: https://kanunmonitoring.com/billing-success
✅ Success page displays:
   - "Subscription Active"
   - Subscription details
   - Next billing date
   - Support contact info
```

### Step 4: Check Stripe Dashboard

**Go to:** https://dashboard.stripe.com/customers

**Look for:**
```
Email: munya@kanunmonitoring.com
Status: ✅ Found

Click on customer to view:
✅ Customer created with correct email
✅ Subscription status: "trialing" (not "active" yet)
✅ Current period ends: 14 days from today
✅ Trial ends at: [Date 14 days from now]
✅ Next billing date: [14 days from now]
✅ Amount: $39.00 USD
```

### Step 5: Check Webhook Logs

**Go to:** Netlify Dashboard > Functions > webhooks-stripe

**Expected Logs:**
```
✅ Event 1: checkout.session.completed
   - Timestamp: Just now
   - Customer email: munya@kanunmonitoring.com

✅ Event 2: customer.subscription.created
   - Subscription status: trialing
   - Trial ends at: [14 days from now]

✅ Event 3: invoice.created
   - Amount: $0.00 (trial invoice)
   - Status: paid
```

### Step 6: Verify Different Tier

**Repeat Steps 1-5 but with:**
- Select **Agency** tier ($79/month)
- Use different email OR just proceed with munya@ again
- Verify correct price in Stripe

**Expected in Stripe:**
```
✅ New subscription for Agency tier
✅ Amount: $79.00 USD
✅ Status: trialing
✅ Trial ends: 14 days from today
```

### Step 7: Test Cancellation (Optional)

**Go to:** https://dashboard.stripe.com/subscriptions

**Find:** Subscription for munya@kanunmonitoring.com

**Click subscription → "..." menu → "Cancel subscription"**

**Expected:**
```
✅ Subscription status changes to "canceled"
✅ Webhook fires: customer.subscription.deleted
✅ Check Netlify logs for the event
```

---

## 📊 COMPLETE TEST CHECKLIST

Before considering the setup "complete," verify:

### Website & Checkout
- [ ] Home page loads at https://kanunmonitoring.com
- [ ] Pricing section visible
- [ ] All 3 pricing cards display
- [ ] Buttons are clickable and working
- [ ] Stripe Checkout page loads when button clicked
- [ ] Checkout page shows correct price & trial info

### Payment Processing
- [ ] Card `4242 4242 4242 4242` is accepted
- [ ] Redirects to `/billing-success` after payment
- [ ] Success page shows subscription details
- [ ] Email address is captured correctly
- [ ] Trial period shows 14 days

### Stripe Integration
- [ ] Customer record created in Stripe Dashboard
- [ ] Subscription shows status: "trialing"
- [ ] Trial end date is 14 days from now
- [ ] Next billing date is correct
- [ ] Payment method is saved

### Webhooks
- [ ] `checkout.session.completed` event received
- [ ] `customer.subscription.created` event received
- [ ] `invoice.created` event received
- [ ] All events visible in Netlify function logs
- [ ] Webhook signature verification passes

### Email Workflow (Manual for now)
- [ ] Day 0: Welcome email sent (needs backend)
- [ ] Day 10: Trial expiring reminder (needs backend)
- [ ] Day 12: Last chance email (needs backend)
- [ ] Day 14: Conversion confirmation (needs backend)

---

## 🎯 TEST RESULTS SUMMARY

Create this document after testing:

```markdown
# Test Results — [Date]

## Basic Functionality
- [x] Website loads at kanunmonitoring.com
- [x] Pricing section displays all 3 tiers
- [x] Checkout buttons are functional

## Checkout Test (Solo Monitor)
- [x] Stripe Checkout page loads
- [x] Correct price displayed ($39/month)
- [x] 14-day trial period shown
- [x] Payment processing succeeds
- [x] Redirects to /billing-success

## Stripe Integration
- [x] Customer created: munya@kanunmonitoring.com
- [x] Subscription status: trialing
- [x] Trial end date: [Correct date 14 days away]
- [x] Next billing: [Correct date 14 days away]

## Webhooks
- [x] checkout.session.completed received
- [x] customer.subscription.created received
- [x] invoice.created received
- [x] All events logged in Netlify

## Notes
[Any observations, issues, or next steps]
```

---

## 🚀 AFTER TESTING: NEXT STEPS

### For Production Stability

1. **Monitor Stripe for Issues:**
   - Check dashboard daily for first week
   - Review customer complaints
   - Verify webhook delivery success rate

2. **Set Up Alerts:**
   - Stripe webhook failures: Set up Slack notification
   - Payment failures: Track and follow up
   - Chargeback alerts: Monitor and respond

3. **Build Backend for Trial Management:**
   - Create database schema for subscriptions
   - Implement trial expiration job (runs daily)
   - Send reminder emails on days 10, 12, 13
   - Update status to "active" on day 14 charge

4. **Email Templates:**
   - Day 0: Welcome
   - Day 10: Trial expiring soon
   - Day 12: Last chance
   - Day 13: Final reminder
   - Day 14: Welcome to paid subscription

5. **Monitor Conversion Metrics:**
   - Trial sign-ups: # per day
   - Trial-to-paid conversion rate: % who don't cancel
   - Average customer lifetime value
   - Churn rate

---

## ❌ TROUBLESHOOTING

### Problem: Checkout button doesn't work

**Check:**
1. Is the site actually kanunmonitoring.com or still netlify.app?
2. Are environment variables set? (STRIPE_SECRET_KEY)
3. Check browser console for JavaScript errors
4. Check Netlify function logs for errors

**Solution:**
```bash
cd /Users/geoffrey/kanun-monitoring-next
netlify env:list  # Verify STRIPE_SECRET_KEY is set
netlify deploy --prod  # Redeploy
```

### Problem: Payment fails

**Check:**
1. Is Stripe in LIVE mode? (not test mode)
2. Is the account verified with real bank account?
3. Is the card supported in your region?

**Solution:**
- Go to https://dashboard.stripe.com
- Check account status in settings
- Verify account is in "Live" mode

### Problem: Webhook not firing

**Check:**
1. Is webhook endpoint actually enabled in Stripe?
2. Is the URL correct? Should be: `https://kanunmonitoring.com/.netlify/functions/webhooks-stripe`
3. Are there errors in Netlify function logs?

**Solution:**
```bash
# Verify webhook in Stripe
1. Go to: https://dashboard.stripe.com/webhooks
2. Click endpoint: we_1TtHiLBryn2IZeeR8YjmcW3G
3. Check "Last response" for any errors
4. Resend event for testing
```

### Problem: Billing success page doesn't load

**Check:**
1. Is `/billing-success.html` deployed?
2. Is the URL exactly `/billing-success`?
3. Are there any 404 errors in Netlify logs?

**Solution:**
```bash
cd /Users/geoffrey/kanun-monitoring-next
netlify deploy --prod
```

---

## 📞 SUPPORT RESOURCES

| Issue | Where to Check |
|-------|----------------|
| Payment failures | Stripe Dashboard > Payments |
| Webhook delivery | Stripe Dashboard > Webhooks > [endpoint] |
| Webhook logs | Netlify Dashboard > Functions > webhooks-stripe |
| Subscription status | Stripe Dashboard > Subscriptions |
| Customer info | Stripe Dashboard > Customers |

---

## ✅ SIGN-OFF

Once you've completed all tests and verified everything works:

```
Date Tested: ___________
Tested By: Geoffrey Butler (munya@kanunmonitoring.com)

All Checks Passed: [ ] Yes [ ] No

Issues Found: 
[List any issues]

Approved for Production: [ ] Yes [ ] No
```

---

## 🎊 READY FOR CUSTOMERS!

Once testing is complete and all items checked, your KaNun Monitoring platform is ready to accept real customer payments on https://kanunmonitoring.com
