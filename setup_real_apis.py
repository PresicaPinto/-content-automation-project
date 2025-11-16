#!/usr/bin/env python3
"""
Real API Setup and Configuration Guide
Sets up LinkedIn and Twitter APIs for real-time data fetching
"""

import os
from pathlib import Path
import json
from dotenv import load_dotenv, set_key

def setup_api_credentials():
    """
    Interactive setup for LinkedIn and Twitter API credentials
    This will guide you through getting real API access
    """

    print("🔧 Real API Setup for Social Media Analytics")
    print("=" * 50)
    print()

    # Load existing .env file
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv()

    print("📋 To get REAL data from social media APIs, you need to:")
    print()

    print("🐦 TWITTER/X API SETUP:")
    print("1. Go to https://developer.twitter.com/")
    print("2. Create a new App or use existing one")
    print("3. Get your credentials from the App dashboard")
    print("4. You'll need:")
    print("   - Client ID (API Key)")
    print("   - Client Secret (API Secret)")
    print("   - Bearer Token (recommended for read access)")
    print()

    print("💼 LINKEDIN API SETUP:")
    print("1. Go to https://www.linkedin.com/developers/apps/new")
    print("2. Create a new application")
    print("3. Get your credentials from the app dashboard")
    print("4. You'll need:")
    print("   - Client ID")
    print("   - Client Secret")
    print("   - Access Token (if you have one)")
    print()

    # Interactive input for credentials
    setup_credentials = input("Do you want to set up API credentials now? (y/n): ").lower().strip()

    if setup_credentials == 'y':
        print("\n🔑 Twitter/X API Credentials:")
        twitter_client_id = input("Twitter Client ID (API Key): ").strip()
        twitter_client_secret = input("Twitter Client Secret (API Secret): ").strip()
        twitter_bearer_token = input("Twitter Bearer Token (optional): ").strip()

        print("\n🔑 LinkedIn API Credentials:")
        linkedin_client_id = input("LinkedIn Client ID: ").strip()
        linkedin_client_secret = input("LinkedIn Client Secret: ").strip()
        linkedin_access_token = input("LinkedIn Access Token (optional): ").strip()

        # Save credentials to .env file
        print("\n💾 Saving credentials to .env file...")

        env_updates = {
            'TWITTER_CLIENT_ID': twitter_client_id,
            'TWITTER_CLIENT_SECRET': twitter_client_secret,
            'TWITTER_BEARER_TOKEN': twitter_bearer_token,
            'LINKEDIN_CLIENT_ID': linkedin_client_id,
            'LINKEDIN_CLIENT_SECRET': linkedin_client_secret,
            'LINKEDIN_ACCESS_TOKEN': linkedin_access_token
        }

        for key, value in env_updates.items():
            if value:  # Only save non-empty values
                set_key('.env', key, value)

        print("✅ Credentials saved to .env file!")
        print("\n🔄 Restart the dashboard to use real API data!")

    else:
        print("\n⚠️  Without API credentials, the dashboard will use simulated data.")
        print("📖 You can add credentials later by editing the .env file")
        print("🌐 Or visit the dashboard and use the configuration modal")

    print()
    print("📊 Dashboard is running at: http://127.0.0.1:5001")
    print("🔧 You can configure Twitter/LinkedIn usernames in the dashboard")

def create_demo_config():
    """Create a demo configuration with sample accounts"""

    demo_config = {
        "twitter_accounts": [
            {
                "username": "elonmusk",
                "display_name": "Elon Musk",
                "description": "CEO of Tesla, SpaceX"
            },
            {
                "username": "sundarpichai",
                "display_name": "Sundar Pichai",
                "description": "CEO of Alphabet/Google"
            },
            {
                "username": "satyanadella",
                "display_name": "Satya Nadella",
                "description": "CEO of Microsoft"
            }
        ],
        "linkedin_companies": [
            {
                "company_id": "1441",
                "display_name": "Microsoft",
                "description": "Technology company"
            },
            {
                "company_id": "162479",
                "display_name": "Google",
                "description": "Technology company"
            },
            {
                "company_id": "1035",
                "display_name": "Tesla",
                "description": "Electric vehicle company"
            }
        ],
        "monitoring_settings": {
            "update_interval": 60,
            "enable_alerts": True,
            "alert_thresholds": {
                "engagement_spike": 50.0,
                "follower_drop": -10.0,
                "viral_threshold": 1000
            }
        }
    }

    # Save demo config
    with open('demo_config.json', 'w') as f:
        json.dump(demo_config, f, indent=2)

    print("📋 Created demo_config.json with sample accounts")

def test_api_connections():
    """Test if API connections are working"""

    print("\n🧪 Testing API connections...")

    # Import after setting up environment
    from twitter_real_api import twitter_real_api, test_twitter_connection
    from linkedin_real_api import linkedin_real_api, test_linkedin_connection

    # Test Twitter
    twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
    twitter_client_secret = os.getenv('TWITTER_CLIENT_SECRET')
    twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if twitter_client_id and twitter_client_secret:
        try:
            twitter_real_api.setup_with_credentials(
                twitter_client_id,
                twitter_client_secret,
                twitter_bearer_token
            )

            # Test connection
            if test_twitter_connection():
                print("✅ Twitter API connection successful!")
            else:
                print("❌ Twitter API connection failed")
        except Exception as e:
            print(f"❌ Twitter API error: {e}")
    else:
        print("⚠️  Twitter API credentials not configured")

    # Test LinkedIn
    linkedin_client_id = os.getenv('LINKEDIN_CLIENT_ID')
    linkedin_client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    linkedin_access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    if linkedin_client_id and linkedin_client_secret:
        try:
            linkedin_real_api.setup_with_credentials(
                linkedin_client_id,
                linkedin_client_secret,
                linkedin_access_token
            )

            # Test with a sample company ID
            if test_linkedin_connection("1441"):  # Microsoft
                print("✅ LinkedIn API connection successful!")
            else:
                print("❌ LinkedIn API connection failed")
        except Exception as e:
            print(f"❌ LinkedIn API error: {e}")
    else:
        print("⚠️  LinkedIn API credentials not configured")

def show_dashboard_info():
    """Show information about accessing the dashboard"""

    print("\n🌐 Dashboard Access Information:")
    print("=" * 40)
    print("📊 Main Dashboard: http://127.0.0.1:5001")
    print("🌍 Network Access: http://172.29.89.92:5001")
    print()
    print("✨ Dashboard Features:")
    print("  🔄 Real-time metrics updates")
    print("  📈 Interactive charts and trends")
    print("  🚨 Smart alerts and notifications")
    print("  💡 Performance insights and recommendations")
    print("  ⚙️  Configurable monitoring settings")
    print()
    print("🎯 Quick Start:")
    print("  1. Open the dashboard URL in your browser")
    print("  2. Click 'Start Monitoring' button")
    print("  3. Configure Twitter/LinkedIn accounts if needed")
    print("  4. Watch real-time data flow in!")
    print()
    print("📱 The dashboard works on mobile devices too!")

if __name__ == "__main__":
    # Create demo configuration
    create_demo_config()

    # Setup API credentials
    setup_api_credentials()

    # Test connections (will use fallback data if no credentials)
    test_api_connections()

    # Show dashboard access info
    show_dashboard_info()

    print("\n🎉 Setup complete! Enjoy your real-time social media analytics dashboard!")