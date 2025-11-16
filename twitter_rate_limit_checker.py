#!/usr/bin/env python3
"""
Twitter Rate Limit Checker - Check API status and remaining requests
"""

import os
import sys
import requests
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_twitter_rate_limits():
    """Check Twitter API rate limits and status"""
    print("🔍 Twitter API Rate Limit Checker")
    print("=" * 50)

    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("❌ Bearer Token not found")
        return

    print(f"✅ Bearer Token: {bearer_token[:20]}...")

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    # Test API with a simple request to get rate limit info
    try:
        print("\n🔍 Testing API with rate limit check...")

        # Try to get rate limit info
        response = requests.get(
            "https://api.twitter.com/2/users/by/username/twitter",
            headers=headers
        )

        print(f"Status Code: {response.status_code}")

        # Check rate limit headers
        rate_limit_remaining = response.headers.get('x-rate-limit-remaining', 'Unknown')
        rate_limit_reset = response.headers.get('x-rate-limit-reset', 'Unknown')
        rate_limit_limit = response.headers.get('x-rate-limit-limit', 'Unknown')

        print(f"Rate Limit Info:")
        print(f"   Limit: {rate_limit_remaining}/{rate_limit_limit} requests remaining")

        if rate_limit_reset != 'Unknown':
            reset_time = datetime.fromtimestamp(int(rate_limit_reset))
            print(f"   Reset Time: {reset_time}")

        if response.status_code == 200:
            print("✅ API is working correctly")
            data = response.json()
            if 'data' in data:
                user = data['data']
                print(f"   Test User: @{user['username']} ({user.get('name')})")
                print(f"   Followers: {user['public_metrics']['followers_count']:,}")
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded")
            if rate_limit_reset != 'Unknown':
                reset_time = datetime.fromtimestamp(int(rate_limit_reset))
                print(f"   Resets at: {reset_time}")
                now = datetime.now()
                time_to_reset = reset_time - now
                print(f"   Time to reset: {time_to_reset}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error checking rate limits: {str(e)}")

def wait_for_rate_limit_reset():
    """Wait for rate limit to reset (if needed)"""
    print("\n⏳ Rate Limit Reset Helper")
    print("=" * 30)
    print("If you're rate limited, you can:")
    print("1. Wait ~15 minutes for automatic reset")
    print("2. Use a different Twitter Developer App")
    print("3. Upgrade your API plan for higher limits")
    print("4. Try again later")

if __name__ == "__main__":
    check_twitter_rate_limits()
    wait_for_rate_limit_reset()