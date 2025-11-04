#!/usr/bin/env python3
"""
LinkedIn Connection Test for Ardelis Technologies
Tests if Buffer is connected to LinkedIn
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from scheduler import SocialMediaScheduler

def test_linkedin_connection():
    """Test if LinkedIn is connected through Buffer"""
    print("🔗 Testing LinkedIn Connection via Buffer API")
    print("=" * 50)

    # Load environment variables
    load_dotenv('config/.env.production')

    # Check for Buffer access token
    buffer_token = os.getenv('BUFFER_ACCESS_TOKEN')

    if not buffer_token:
        print("❌ BUFFER_ACCESS_TOKEN not found")
        print("💡 Add this to config/.env.production:")
        print("   BUFFER_ACCESS_TOKEN=your_buffer_access_token")
        return False

    print("✅ BUFFER_ACCESS_TOKEN found")

    # Initialize scheduler
    try:
        scheduler = SocialMediaScheduler(buffer_token)
        print("✅ Buffer scheduler initialized")
    except Exception as e:
        print(f"❌ Error initializing Buffer scheduler: {e}")
        return False

    # Test Buffer API connection
    print("🌐 Testing Buffer API connection...")
    try:
        profiles = scheduler.get_profiles()

        if profiles is None:
            print("❌ Failed to connect to Buffer API")
            print("💡 Check your internet connection and token")
            return False

        print(f"✅ Connected to Buffer API!")
        print(f"📱 Found {len(profiles)} connected profiles:")

        linkedin_found = False
        for profile in profiles:
            service = profile.get('service', '').lower()
            if service == 'linkedin':
                linkedin_found = True
                print(f"   ✅ LinkedIn: {profile.get('formatted_username', 'N/A')} ({profile.get('id', 'N/A')})")
            else:
                print(f"   📱 {service.capitalize()}: {profile.get('formatted_username', 'N/A')}")

        if not linkedin_found:
            print("⚠️  No LinkedIn profile found in Buffer")
            print("💡 Connect your LinkedIn account to Buffer")
            print("   1. Go to https://buffer.com")
            print("   2. Connect your LinkedIn account")
            print("   3. Refresh this test")
            return False

        print("\n🎉 LinkedIn is connected through Buffer!")
        print("📅 Your scheduled posts will be published automatically")

        return True

    except Exception as e:
        print(f"❌ Error testing Buffer API: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 LinkedIn Connection Test for Ardelis Technologies")
    print("=" * 60)

    success = test_linkedin_connection()

    if success:
        print("\n✅ LinkedIn is ready for automated posting!")
        print("🔗 Posts scheduled in your calendar will be published automatically")
        print("📊 You can track performance in the dashboard")
    else:
        print("\n❌ LinkedIn connection test failed")
        print("🔧 Please fix the issues above and try again")
        print("💡 See https://buffer.com/help for connection help")

    return success

if __name__ == '__main__':
    main()