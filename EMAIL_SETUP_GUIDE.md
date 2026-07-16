# 📧 Email Setup Guide — KaNun Monitoring

**Goal:** All emails to any address @kanunmonitoring.com → munya@kanunmonitoring.com  
**Also:** Update Stripe invoices to show help@kanunmonitoring.com instead of mkanaventi@gmail.com

---

## Step 1: Set Up Google Workspace Catch-All

This allows you to use ANY email address @kanunmonitoring.com and receive it in munya@kanunmonitoring.com.

### Option A: Using Service Account (Recommended)

1. **Get Google Admin Service Account Key:**
   - Go to https://console.cloud.google.com/iam-admin/serviceaccounts
   - Select your project (or create one)
   - Click "Create Service Account"
   - Name: `google-admin-api`
   - Grant roles: `Editor` or `Directory API Admin`
   - Create JSON key and download

2. **Run the setup script:**
   ```bash
   python3 setup-email-catchall.py /path/to/service-account-key.json
   ```

3. **What it does:**
   - Creates a group: `help@kanunmonitoring.com`
   - Adds `munya@kanunmonitoring.com` as a member
   - All emails to @kanunmonitoring.com are caught by this group

### Option B: Using OAuth (Manual)

1. **Run with OAuth flag:**
   ```bash
   python3 setup-email-catchall.py --oauth
   ```

2. **Browser will open** — sign in with munya@kanunmonitoring.com
3. **Grant permissions** for Directory API

---

## Step 2: Update Stripe Invoice Email

Once the Google catch-all is set up, update Stripe to use `help@kanunmonitoring.com`.

### When Ready:

1. **Get your Stripe Live Secret Key**
   - Go to https://dashboard.stripe.com/apikeys
   - Copy your Live Secret Key (starts with `sk_live_`)

2. **Run the Stripe update script:**
   ```bash
   python3 update-stripe-email.py sk_live_51Tq7o4Bryn2IZeeR...
   ```

3. **Verify:**
   - Go to Stripe Dashboard → Settings → Branding
   - Should show: `help@kanunmonitoring.com`

---

## Step 3: Test It

### Test Email Catch-All:

1. **Send test email:**
   ```bash
   echo "Test" | mail -s "Catch-all test" test@kanunmonitoring.com
   ```
   Or use any email client to send to: `test@kanunmonitoring.com`

2. **Check inbox:**
   - Open munya@kanunmonitoring.com
   - Should receive the email

### Test Stripe:

1. **In Stripe Dashboard:**
   - Create a test invoice
   - Check footer — should say "Contact us at help@kanunmonitoring.com"

2. **Send test email to Stripe support address:**
   - Send email to: `help@kanunmonitoring.com`
   - Should arrive in: `munya@kanunmonitoring.com`

---

## File Locations

```
~/kanun-monitoring-next/
├── setup-email-catchall.py      ← Google Workspace setup
├── update-stripe-email.py       ← Stripe email update
└── EMAIL_SETUP_GUIDE.md         ← This file
```

---

## Troubleshooting

### "No credentialed accounts" error

**Solution:** Use service account key method (Option A)

### Group already exists

**Expected behavior** — script will skip creation and add the member

### Stripe API error: "Invalid API Key"

**Solution:** Make sure you're using the LIVE secret key (starts with `sk_live_`)

### Email not arriving in munya@kanunmonitoring.com

**Check:**
1. Is the group visible in Google Admin → Groups?
2. Is munya@kanunmonitoring.com a member of the help@kanunmonitoring.com group?
3. Check Gmail spam folder

---

## Summary

| Step | Action | Email | Result |
|------|--------|-------|--------|
| 1 | Create catch-all group | help@kanunmonitoring.com | Any @kanunmonitoring.com → munya |
| 2 | Update Stripe branding | help@kanunmonitoring.com | Invoices show help@ address |
| 3 | Test both | test@kanunmonitoring.com | Lands in munya inbox |

---

## Commands Reference

```bash
# Set up Google catch-all (with service account)
python3 setup-email-catchall.py /path/to/service-account-key.json

# Set up Google catch-all (with OAuth)
python3 setup-email-catchall.py --oauth

# Update Stripe email
python3 update-stripe-email.py sk_live_51Tq7o4Bryn2IZeeR...

# Test email manually
echo "Test email" | mail -s "Test" any-address@kanunmonitoring.com
```
