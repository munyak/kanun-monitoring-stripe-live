#!/usr/bin/env python3
"""
Update Stripe account branding email to help@kanunmonitoring.com

Usage:
  python3 update-stripe-email.py <stripe-live-secret-key>

This updates:
- support_email: help@kanunmonitoring.com (appears on invoices, receipts, etc.)
"""

import sys
import json
import urllib.request
import base64

def update_stripe_email(stripe_secret_key):
    """Update Stripe account support email via API"""
    
    if not stripe_secret_key.startswith('sk_live_'):
        print("❌ Error: Must use LIVE secret key (starts with sk_live_)")
        return False
    
    url = "https://api.stripe.com/v1/account"
    
    # Create basic auth header
    auth_string = f"{stripe_secret_key}:"
    auth_bytes = auth_string.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Update support email
    data = "settings[branding][support_email]=help@kanunmonitoring.com"
    
    try:
        req = urllib.request.Request(
            url,
            data=data.encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            
            print("="*70)
            print("✅ STRIPE ACCOUNT UPDATED")
            print("="*70)
            print(f"Account ID: {result.get('id')}")
            print(f"Support Email: {result.get('settings', {}).get('branding', {}).get('support_email', 'N/A')}")
            print("\n📧 Invoices will now show: help@kanunmonitoring.com")
            print("📧 Emails to this address route to: munya@kanunmonitoring.com (via catch-all)")
            return True
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        error_data = json.loads(error_body)
        print(f"❌ Stripe API Error: {error_data.get('error', {}).get('message', str(e))}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update-stripe-email.py <stripe-live-secret-key>")
        print("\nExample:")
        print("  python3 update-stripe-email.py sk_live_51Tq7o4Bryn2IZeeR...")
        sys.exit(1)
    
    stripe_key = sys.argv[1]
    
    print("="*70)
    print("🔐 STRIPE ACCOUNT EMAIL UPDATE")
    print("="*70)
    print(f"Key: {stripe_key[:20]}...{stripe_key[-10:]}")
    print(f"New support email: help@kanunmonitoring.com")
    print()
    
    success = update_stripe_email(stripe_key)
    
    if success:
        print("\n" + "="*70)
        print("✅ COMPLETE!")
        print("="*70)
        print("""
Next steps:
1. Test by creating a test invoice in Stripe Dashboard
2. Verify the email shows: help@kanunmonitoring.com
3. Send a test email to help@kanunmonitoring.com
4. Confirm it arrives in munya@kanunmonitoring.com
        """)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
