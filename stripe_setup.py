#!/usr/bin/env python3
"""
KaNun Monitoring — Stripe Subscription Setup Script
Configures products, prices, and checkout for all 3 subscription tiers.

Run: python3 stripe_setup.py [--live]
"""

import stripe
import os
import json
from datetime import datetime

# Configuration
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_YOUR_KEY_HERE')
LIVE_MODE = '--live' in __import__('sys').argv

# Initialize Stripe
stripe.api_key = STRIPE_API_KEY
stripe.verify_ssl_certs = True

# Product & Pricing Configuration from KaNun_Monitoring_Client_Info.pdf
PRODUCTS = {
    'solo_monitor': {
        'name': 'Solo Monitor',
        'description': 'Full mobile platform for independent supervised visitation monitors',
        'price': 3900,  # $39.00/month in cents
        'billing_period': 'month',
        'features': [
            'Full mobile platform',
            'Client intake & case management',
            'Visit docs with GPS',
            'Standardized reports',
            'Email auto-filing'
        ]
    },
    'agency': {
        'name': 'Agency',
        'description': 'Everything in Solo Monitor plus team management and agency analytics',
        'price': 7900,  # $79.00/month in cents
        'billing_period': 'month',
        'features': [
            'Everything in Solo Monitor',
            'Up to 5 monitor accounts',
            'Agency dashboard & analytics',
            'Caseload management',
            'Team scheduling'
        ]
    },
    'agency_pro': {
        'name': 'Agency Pro',
        'description': 'Unlimited monitors, advanced analytics, custom report branding, and priority support',
        'price': 14900,  # $149.00/month in cents
        'billing_period': 'month',
        'features': [
            'Everything in Agency',
            'Unlimited monitor accounts',
            'Advanced analytics',
            'Priority support',
            'Custom report branding'
        ],
        'popular': True
    }
}

KCM_CERTIFICATION = {
    'name': 'KCM Certification',
    'description': 'KaNun Certified Monitor credential (initial + annual renewal)',
    'initial_fee': 49900,  # $499.00 in cents
    'renewal_fee': 14900,  # $149.00/year in cents
}

def create_products():
    """Create all subscription products in Stripe"""
    print(f"\n{'='*70}")
    print(f"CREATING PRODUCTS ({'LIVE' if LIVE_MODE else 'TEST'} MODE)")
    print(f"{'='*70}")
    
    products = {}
    
    for key, product_config in PRODUCTS.items():
        try:
            product = stripe.Product.create(
                name=product_config['name'],
                description=product_config['description'],
                type='service',
                metadata={
                    'kanun_tier': key,
                    'created_date': datetime.now().isoformat()
                }
            )
            products[key] = product
            print(f"\n✓ Created product: {product_config['name']}")
            print(f"  Product ID: {product.id}")
            
        except stripe.error.StripeError as e:
            print(f"\n✗ Error creating {product_config['name']}: {e.user_message}")
            return None
    
    return products

def create_prices(products):
    """Create prices for each product"""
    print(f"\n{'='*70}")
    print(f"CREATING PRICES")
    print(f"{'='*70}")
    
    prices = {}
    
    for key, product_config in PRODUCTS.items():
        try:
            price = stripe.Price.create(
                product=products[key].id,
                unit_amount=product_config['price'],
                currency='usd',
                recurring={
                    'interval': product_config['billing_period'],
                    'interval_count': 1,
                    'trial_period_days': 14  # Free 14-day trial
                },
                metadata={
                    'kanun_tier': key,
                    'display_name': product_config['name']
                }
            )
            prices[key] = price
            print(f"\n✓ Created price for {product_config['name']}")
            print(f"  Price ID: {price.id}")
            print(f"  Amount: ${product_config['price']/100:.2f}/{product_config['billing_period']}")
            print(f"  Trial: 14 days free")
            
        except stripe.error.StripeError as e:
            print(f"\n✗ Error creating price for {product_config[name]}: {e.user_message}")
            return None
    
    return prices

def save_configuration(products, prices):
    """Save product and price IDs to a config file"""
    config = {
        'stripe_mode': 'live' if LIVE_MODE else 'test',
        'created_at': datetime.now().isoformat(),
        'products': {},
        'prices': {},
    }
    
    for key in products:
        config['products'][key] = {
            'product_id': products[key].id,
            'name': products[key].name,
        }
        config['prices'][key] = {
            'price_id': prices[key].id,
            'amount': prices[key].unit_amount,
            'currency': prices[key].currency,
        }
    
    filename = f"stripe_config_{('live' if LIVE_MODE else 'test')}.json"
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Configuration saved to {filename}")
    return config

def display_next_steps(config):
    """Display instructions for next steps"""
    print(f"\n{'='*70}")
    print("NEXT STEPS")
    print(f"{'='*70}")
    
    print("\n1. CREATE CHECKOUT PAGES")
    print("   Success: https://kanunmonitoring.com/billing-success")
    print("   Cancel:  https://kanunmonitoring.com/billing-cancel")
    print("   ✓ DONE — pages created in /kanun-monitoring-next/")
    
    print("\n2. CREATE CHECKOUT SESSIONS")
    print("   Use the Price IDs below to create checkout sessions:")
    for tier, data in config['prices'].items():
        print(f"   {tier.upper()}: {data['price_id']}")
    
    print("\n3. SAMPLE CHECKOUT CREATION (Python):")
    print("""
    import stripe
    
    session = stripe.checkout.Session.create(
        mode='subscription',
        success_url='https://kanunmonitoring.com/billing-success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://kanunmonitoring.com/billing-cancel',
        line_items=[
            {
                'price': 'price_XXXXX',  # Use Price ID from above
                'quantity': 1,
            },
        ],
    )
    
    # Redirect customer to checkout
    print(session.url)
    """)
    
    print("\n4. SET UP WEBHOOKS")
    print("   Events to listen for:")
    print("   - checkout.session.completed")
    print("   - customer.subscription.created")
    print("   - customer.subscription.updated")
    print("   - customer.subscription.deleted")
    print("   - invoice.payment_succeeded")
    print("   - invoice.payment_failed")
    
    print("\n5. CONFIGURE WEBHOOK ENDPOINT")
    print("   Endpoint URL: https://api.kanunmonitoring.com/webhooks/stripe")
    print("   (Create this endpoint in your backend to handle events)")

def main():
    print(f"\n{'='*70}")
    print("KaNun Monitoring — Stripe Subscription Setup")
    print(f"Mode: {'LIVE' if LIVE_MODE else 'TEST'}")
    print(f"{'='*70}")
    
    if not STRIPE_API_KEY or 'sk_test' not in STRIPE_API_KEY and 'sk_live' not in STRIPE_API_KEY:
        print("\n✗ Error: STRIPE_SECRET_KEY environment variable not set or invalid")
        print("\n  To set it:")
        print("  export STRIPE_SECRET_KEY='sk_live_YOUR_KEY_HERE'")
        return
    
    print(f"\nUsing API Key: {STRIPE_API_KEY[:20]}...")
    
    # Create products
    products = create_products()
    if not products:
        print("\n✗ Failed to create products. Aborting.")
        return
    
    # Create prices
    prices = create_prices(products)
    if not prices:
        print("\n✗ Failed to create prices. Aborting.")
        return
    
    # Save configuration
    config = save_configuration(products, prices)
    
    # Display next steps
    display_next_steps(config)
    
    print(f"\n{'='*70}")
    print("✓ SETUP COMPLETE")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
