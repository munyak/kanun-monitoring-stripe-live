#!/usr/bin/env python3
"""
Set up Google Workspace catchall: any email to kanunmonitoring.com → munya@kanunmonitoring.com

This script:
1. Creates a catch-all group (help@kanunmonitoring.com)
2. Routes all unmatched emails to munya@kanunmonitoring.com

Requires: Google Admin API credentials (service account or OAuth)

SETUP:
1. Download your Google Admin service account JSON from Google Cloud Console
2. Run: python3 setup-email-catchall.py /path/to/service-account-key.json

OR use OAuth:
   python3 setup-email-catchall.py --oauth
"""

import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.flow import InstalledAppFlow
from google.auth.oauthlib.flow import Flow
import googleapiclient.discovery

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.group.member',
]

DOMAIN = 'kanunmonitoring.com'
CATCHALL_EMAIL = 'help@kanunmonitoring.com'
TARGET_EMAIL = 'munya@kanunmonitoring.com'
ADMIN_EMAIL = 'munya@kanunmonitoring.com'  # Your admin account

def get_credentials(service_account_file=None):
    """Get Google Admin API credentials"""
    if service_account_file:
        # Service account auth
        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES,
            subject=ADMIN_EMAIL  # Impersonate admin
        )
        return creds
    else:
        # OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES
        )
        creds = flow.run_local_server(port=0)
        return creds

def setup_catchall_group(service):
    """Create a catch-all group and add the target email"""
    print(f"\n🔧 Setting up catch-all group: {CATCHALL_EMAIL}")
    
    try:
        # Check if group exists
        results = service.groups().list(domain=DOMAIN).execute()
        groups = results.get('groups', [])
        group = next((g for g in groups if g['email'] == CATCHALL_EMAIL), None)
        
        if group:
            print(f"✅ Group already exists: {CATCHALL_EMAIL}")
            group_key = group['id']
        else:
            # Create group
            group_body = {
                'email': CATCHALL_EMAIL,
                'name': 'Help Desk / Catch-all',
                'description': 'Catch-all group for kanunmonitoring.com - routes to munya@kanunmonitoring.com',
            }
            group = service.groups().insert(body=group_body).execute()
            print(f"✅ Created group: {CATCHALL_EMAIL}")
            group_key = group['id']
        
        # Add target email to group
        member_body = {
            'email': TARGET_EMAIL,
            'role': 'MEMBER',
        }
        
        try:
            service.members().insert(groupKey=group_key, body=member_body).execute()
            print(f"✅ Added {TARGET_EMAIL} to group")
        except Exception as e:
            if 'Member already exists' in str(e):
                print(f"✅ {TARGET_EMAIL} already in group")
            else:
                raise
        
        print(f"\n✅ CATCH-ALL CONFIGURED!")
        print(f"   Group: {CATCHALL_EMAIL}")
        print(f"   Routes to: {TARGET_EMAIL}")
        print(f"\n   All emails sent to any address @{DOMAIN} will be caught by this group.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up catch-all: {e}")
        return False

def main():
    service_account_file = None
    
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == '--oauth':
            print("🔐 Using OAuth flow...")
        else:
            service_account_file = sys.argv[1]
            print(f"🔑 Using service account: {service_account_file}")
    
    try:
        creds = get_credentials(service_account_file)
        service = googleapiclient.discovery.build('admin', 'directory_v1', credentials=creds)
        
        print("="*70)
        print("📧 GOOGLE WORKSPACE CATCH-ALL SETUP")
        print("="*70)
        print(f"Domain: {DOMAIN}")
        print(f"Catch-all email: {CATCHALL_EMAIL}")
        print(f"Routes to: {TARGET_EMAIL}")
        
        success = setup_catchall_group(service)
        
        if success:
            print("\n" + "="*70)
            print("📋 NEXT STEPS:")
            print("="*70)
            print("""
1. In Gmail, you may want to create filters for specific addresses:
   - To access emails sent to specific addresses, use Gmail filters
   - Or check the group settings in Google Admin Console

2. Test it:
   - Send test email to test@kanunmonitoring.com
   - Check if it arrives in munya@kanunmonitoring.com

3. For Stripe:
   - Update support_email to: help@kanunmonitoring.com
   - Run: python3 update-stripe-email.py <your-stripe-live-secret-key>
            """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
