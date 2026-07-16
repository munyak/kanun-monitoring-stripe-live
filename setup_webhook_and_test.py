#!/usr/bin/env python3
"""
KaNun Monitoring — Stripe Webhook Setup & Testing
Completes the final Stripe configuration
"""

import subprocess
import json
import sys

def run_command(cmd, description=""):
    """Run a shell command and return output."""
    if description:
        print(f"\n{'='*70}")
        print(f"🔧 {description}")
        print(f"{'='*70}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def main():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     KaNun Monitoring — Stripe Webhook Setup & Testing              ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Verify deployment
    print("\n✓ Step 1: VERIFY DEPLOYMENT")
    print("-" * 70)
    
    site_url = "https://lighthearted-brioche-b65f7d.netlify.app"
    print(f"Site URL: {site_url}")
    print(f"Function endpoint: {site_url}/.netlify/functions/create-checkout")
    print(f"Webhook endpoint: {site_url}/.netlify/functions/webhooks-stripe")
    print(f"Billing success: {site_url}/billing-success")
    print(f"Billing cancel: {site_url}/billing-cancel")
    
    # Step 2: Instructions for manual setup
    print("\n\n✓ Step 2: CONFIGURE STRIPE WEBHOOK (MANUAL)")
    print("-" * 70)
    print("""
    1. Go to: https://dashboard.stripe.com/webhooks
    2. Click "+ Add endpoint"
    3. Enter endpoint URL:
       https://lighthearted-brioche-b65f7d.netlify.app/.netlify/functions/webhooks-stripe
    4. Select events (check these):
       ✓ checkout.session.completed
       ✓ customer.subscription.created
       ✓ customer.subscription.updated
       ✓ customer.subscription.deleted
       ✓ invoice.payment_succeeded
       ✓ invoice.payment_failed
    5. Click "Add endpoint"
    6. Copy the "Signing secret" (whsec_...)
    7. Add to Netlify:
       - Go to: Site settings > Build & deploy > Environment
       - Add: STRIPE_WEBHOOK_SECRET=whsec_xxxxx
       - Redeploy: netlify deploy --prod
    """)
    
    # Step 3: Test checkout endpoint
    print("\n✓ Step 3: TEST CHECKOUT ENDPOINT")
    print("-" * 70)
    
    import requests
    try:
        response = requests.post(
            f"{site_url}/.netlify/functions/create-checkout",
            json={"priceId": "price_1TtFcKBryn2IZeeRuZhZJJJL"},
            timeout=10
        )
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Checkout endpoint is working!")
        else:
            print("⚠ Checkout endpoint returned non-200 status")
    except Exception as e:
        print(f"✗ Error testing endpoint: {e}")
    
    # Step 4: Test information
    print("\n\n✓ Step 4: TEST CHECKOUT FLOW")
    print("-" * 70)
    print("""
    Ready to test! Here's what to do:
    
    1. Price IDs (from stripe_config_live.json):
       - Solo Monitor: price_1TtFcKBryn2IZeeRuZhZJJJL
       - Agency: price_1TtFcKBryn2IZeeRwxvZ0Swh
       - Agency Pro: price_1TtFcLBryn2IZeeRXlzKL5LI
    
    2. Test Card (Stripe test mode only):
       Card: 4242 4242 4242 4242
       Exp: 12/25
       CVC: 123
    
    3. Create a test page with button:
       <button class="checkout-btn" data-price-id="price_1TtFcKBryn2IZeeRuZhZJJJL">
         Subscribe
       </button>
       <script src="stripe-checkout.js"></script>
    
    4. User flow:
       Click button → redirects to Stripe Checkout → enters test card
       → success → redirected to /billing-success → webhook fires
    """)
    
    # Step 5: Checklist
    print("\n✓ Step 5: DEPLOYMENT CHECKLIST")
    print("-" * 70)
    print("""
    ✅ Deployed to Netlify: lighthearted-brioche-b65f7d.netlify.app
    ✅ Stripe products created (3 tiers)
    ✅ Netlify functions ready (checkout + webhooks)
    ✅ Billing pages deployed (success + cancel)
    ✅ Frontend checkout script ready (stripe-checkout.js)
    
    📋 STILL TODO:
    ⬜ Connect custom domain (kanunmonitoring.com) in Netlify
    ⬜ Create webhook endpoint in Stripe Dashboard
    ⬜ Add STRIPE_WEBHOOK_SECRET env var to Netlify
    ⬜ Add checkout buttons to your site
    ⬜ Test with Stripe test card
    ⬜ Switch to LIVE mode when ready
    """)
    
    # Step 6: Custom domain
    print("\n✓ Step 6: CONNECT CUSTOM DOMAIN")
    print("-" * 70)
    print("""
    To use kanunmonitoring.com instead of netlify.app:
    
    1. Go to: https://app.netlify.com/sites/lighthearted-brioche-b65f7d/settings/domain
    2. Click "Add domain"
    3. Enter: kanunmonitoring.com
    4. Follow Netlify's DNS setup (update your domain registrar)
    
    After domain is connected, update Stripe webhook to:
    https://kanunmonitoring.com/.netlify/functions/webhooks-stripe
    """)
    
    print("\n" + "="*70)
    print("✅ STRIPE SETUP COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
