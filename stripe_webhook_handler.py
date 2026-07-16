#!/usr/bin/env python3
"""
KaNun Monitoring — Stripe Webhook Handler
Processes Stripe events: subscriptions, payments, refunds

Usage: Add to your FastAPI/Flask backend at /webhooks/stripe
"""

import stripe
import os
import json
from datetime import datetime
from typing import Dict, Any

# Configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

stripe.api_key = STRIPE_SECRET_KEY

# Event Handlers
class StripeEventHandler:
    
    @staticmethod
    def handle_checkout_session_completed(event: Dict[str, Any]):
        """Customer completed checkout — create subscription record"""
        session = event['data']['object']
        
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        customer_email = session.get('customer_details', {}).get('email')
        
        print(f"✓ Checkout completed for {customer_email}")
        print(f"  Subscription ID: {subscription_id}")
        print(f"  Customer ID: {customer_id}")
        
        # TODO: Save to your database
        # User.create_subscription(customer_id=customer_id, subscription_id=subscription_id)
        # Email.send_welcome_email(customer_email)
        
        return {
            'status': 'processed',
            'subscription_id': subscription_id,
            'customer_email': customer_email,
        }
    
    @staticmethod
    def handle_customer_subscription_created(event: Dict[str, Any]):
        """Subscription created — grant platform access"""
        subscription = event['data']['object']
        
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        current_period_start = subscription.get('current_period_start')
        current_period_end = subscription.get('current_period_end')
        
        print(f"✓ Subscription created")
        print(f"  Subscription ID: {subscription_id}")
        print(f"  Status: {status}")
        print(f"  Trial ends: {datetime.fromtimestamp(current_period_end)}")
        
        # TODO: Grant access to platform
        # Subscription.update_status(subscription_id, status='active')
        # User.grant_platform_access(customer_id)
        
        return {
            'status': 'processed',
            'subscription_id': subscription_id,
            'access_granted': True,
        }
    
    @staticmethod
    def handle_customer_subscription_updated(event: Dict[str, Any]):
        """Subscription changed (upgraded, downgraded, etc)"""
        subscription = event['data']['object']
        previous = event['data'].get('previous_attributes', {})
        
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        
        print(f"✓ Subscription updated")
        print(f"  Subscription ID: {subscription_id}")
        print(f"  New status: {status}")
        
        if 'items' in previous:
            print(f"  Plan changed (upgrade/downgrade)")
        
        # TODO: Update subscription record
        # Subscription.update(subscription_id, status=status)
        
        return {
            'status': 'processed',
            'subscription_id': subscription_id,
        }
    
    @staticmethod
    def handle_customer_subscription_deleted(event: Dict[str, Any]):
        """Subscription cancelled"""
        subscription = event['data']['object']
        
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        cancellation_reason = subscription.get('cancellation_details', {}).get('reason')
        
        print(f"✓ Subscription cancelled")
        print(f"  Subscription ID: {subscription_id}")
        print(f"  Reason: {cancellation_reason}")
        
        # TODO: Revoke platform access
        # Subscription.mark_cancelled(subscription_id)
        # User.revoke_platform_access(customer_id)
        # Email.send_goodbye_email(customer_id)
        
        return {
            'status': 'processed',
            'subscription_id': subscription_id,
            'access_revoked': True,
        }
    
    @staticmethod
    def handle_invoice_payment_succeeded(event: Dict[str, Any]):
        """Invoice paid successfully"""
        invoice = event['data']['object']
        
        customer_id = invoice.get('customer')
        invoice_id = invoice.get('id')
        amount_paid = invoice.get('amount_paid')
        
        print(f"✓ Invoice paid")
        print(f"  Invoice ID: {invoice_id}")
        print(f"  Amount: ${amount_paid/100:.2f}")
        
        # TODO: Update payment records
        # Invoice.mark_paid(invoice_id)
        # User.send_receipt(customer_id, invoice_id)
        
        return {
            'status': 'processed',
            'invoice_id': invoice_id,
            'amount_paid': amount_paid,
        }
    
    @staticmethod
    def handle_invoice_payment_failed(event: Dict[str, Any]):
        """Invoice payment failed"""
        invoice = event['data']['object']
        
        customer_id = invoice.get('customer')
        invoice_id = invoice.get('id')
        amount_owed = invoice.get('amount_due')
        
        print(f"⚠ Invoice payment failed")
        print(f"  Invoice ID: {invoice_id}")
        print(f"  Amount owed: ${amount_owed/100:.2f}")
        
        # TODO: Notify customer, retry logic
        # Invoice.mark_failed(invoice_id)
        # Email.send_payment_failed_notice(customer_id, invoice_id)
        
        return {
            'status': 'processed',
            'invoice_id': invoice_id,
            'action': 'sent_payment_reminder',
        }

# Event Type Mapping
EVENT_HANDLERS = {
    'checkout.session.completed': StripeEventHandler.handle_checkout_session_completed,
    'customer.subscription.created': StripeEventHandler.handle_customer_subscription_created,
    'customer.subscription.updated': StripeEventHandler.handle_customer_subscription_updated,
    'customer.subscription.deleted': StripeEventHandler.handle_customer_subscription_deleted,
    'invoice.payment_succeeded': StripeEventHandler.handle_invoice_payment_succeeded,
    'invoice.payment_failed': StripeEventHandler.handle_invoice_payment_failed,
}

# Webhook Endpoint (FastAPI example)
def webhook_handler(request_body: str, stripe_signature: str) -> Dict[str, Any]:
    """
    Verify and process Stripe webhooks.
    
    Usage (FastAPI):
        @app.post('/webhooks/stripe')
        async def stripe_webhook(request: Request):
            body = await request.body()
            signature = request.headers.get('stripe-signature')
            result = webhook_handler(body.decode(), signature)
            return result
    
    Usage (Flask):
        @app.route('/webhooks/stripe', methods=['POST'])
        def stripe_webhook():
            result = webhook_handler(request.data.decode(), request.headers.get('Stripe-Signature'))
            return result
    """
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            request_body,
            stripe_signature,
            STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        print("✗ Invalid request body")
        return {'status': 'error', 'message': 'Invalid request body'}, 400
    except stripe.error.SignatureVerificationError:
        print("✗ Invalid signature")
        return {'status': 'error', 'message': 'Invalid signature'}, 400
    
    event_type = event['type']
    
    print(f"\n{'='*70}")
    print(f"Stripe Webhook: {event_type}")
    print(f"Event ID: {event['id']}")
    print(f"{'='*70}")
    
    # Route to appropriate handler
    handler = EVENT_HANDLERS.get(event_type)
    
    if handler:
        try:
            result = handler(event)
            print(f"✓ Event processed successfully")
            return {'status': 'success', 'result': result}, 200
        except Exception as e:
            print(f"✗ Error processing event: {str(e)}")
            return {'status': 'error', 'message': str(e)}, 500
    else:
        print(f"⚠ Unhandled event type: {event_type}")
        return {'status': 'ignored', 'event_type': event_type}, 200

# Webhook Configuration Instructions
WEBHOOK_SETUP_INSTRUCTIONS = """
STRIPE WEBHOOK SETUP

1. Go to Stripe Dashboard > Developers > Webhooks
2. Click "Add an endpoint"
3. Enter your endpoint URL:
   https://api.kanunmonitoring.com/webhooks/stripe

4. Select events to listen for:
   ✓ checkout.session.completed
   ✓ customer.subscription.created
   ✓ customer.subscription.updated
   ✓ customer.subscription.deleted
   ✓ invoice.payment_succeeded
   ✓ invoice.payment_failed

5. Copy the webhook signing secret (Whsec_...)
6. Add to your .env file:
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

7. Test the webhook:
   stripe listen --forward-to localhost:8000/webhooks/stripe

8. Deploy to production when ready.
"""

if __name__ == '__main__':
    print(WEBHOOK_SETUP_INSTRUCTIONS)
