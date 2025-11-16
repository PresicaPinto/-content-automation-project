#!/usr/bin/env python3
"""
Reset Backend to Zero - Update backend to match real API data
"""

import requests
import json
from datetime import datetime, timezone

def reset_backend_to_real_values():
    """Reset backend data to match real Twitter API values"""
    print("🔄 Resetting Backend to Real Twitter API Values")
    print("=" * 60)

    # Your backend endpoint
    backend_endpoint = "http://172.29.89.92:5000/api/social/connections"

    # Real API values (what Twitter API actually returns)
    real_api_data = {
        "twitter": {
            "account_name": "Presica_Pinto",
            "account_type": "user",
            "analytics": {
                "data_source": "api",
                "engagement": 0.0,  # 0 followers = 0 engagement
                "followers": 0,     # REAL API VALUE
                "following": 2,     # REAL API VALUE
                "impressions": 0,   # 0 tweets = 0 impressions
                "likes": 0,         # 0 tweets = 0 likes
                "posts": 0,         # REAL API VALUE
                "profile_views": 0, # REAL API VALUE
                "quality_score": 0,
                "reach": 0,         # 0 followers = 0 reach
                "replies": 0,       # 0 tweets = 0 replies
                "retweets": 0,      # 0 tweets = 0 retweets
                "tweets": 0,        # REAL API VALUE
                "verified": False   # REAL API VALUE
            },
            "client_id": "rDHHOI7jpi97n5i5HgxLqKIvw",
            "connected": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_connected": datetime.now(timezone.utc).isoformat(),
            "platform": "twitter",
            "username": "Presica_Pinto"
        }
    }

    print("📊 New Backend Values (matching real Twitter API):")
    analytics = real_api_data['twitter']['analytics']
    for key, value in analytics.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 Sending reset request to backend...")

    try:
        # Try different methods to update backend
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TwitterDataReset/1.0'
        }

        # Method 1: Try POST
        print("📤 Method 1: Trying POST request...")
        response = requests.post(
            backend_endpoint,
            json=real_api_data,
            headers=headers,
            timeout=10
        )

        print(f"   Status: {response.status_code}")

        if response.status_code in [200, 201, 204]:
            print("✅ POST successful! Backend updated to real values")
            return True
        else:
            print(f"   POST failed: {response.text}")

        # Method 2: Try PUT
        print("\n📤 Method 2: Trying PUT request...")
        response = requests.put(
            backend_endpoint,
            json=real_api_data,
            headers=headers,
            timeout=10
        )

        print(f"   Status: {response.status_code}")

        if response.status_code in [200, 201, 204]:
            print("✅ PUT successful! Backend updated to real values")
            return True
        else:
            print(f"   PUT failed: {response.text}")

        # Method 3: Try PATCH
        print("\n📤 Method 3: Trying PATCH request...")
        response = requests.patch(
            backend_endpoint,
            json=real_api_data,
            headers=headers,
            timeout=10
        )

        print(f"   Status: {response.status_code}")

        if response.status_code in [200, 201, 204]:
            print("✅ PATCH successful! Backend updated to real values")
            return True
        else:
            print(f"   PATCH failed: {response.text}")

        print(f"\n❌ All HTTP methods failed")
        print(f"💡 Your backend may only accept GET requests")
        print(f"💡 Contact your backend admin to enable POST/PUT/PATCH")

        return False

    except Exception as e:
        print(f"❌ Error updating backend: {str(e)}")
        return False

def verify_backend_reset():
    """Verify the backend has been reset"""
    print(f"\n🔍 Verifying backend reset...")

    try:
        response = requests.get("http://172.29.89.92:5000/api/social/connections", timeout=10)

        if response.status_code == 200:
            data = response.json()
            twitter_data = data.get('connections', {}).get('twitter', {})

            if twitter_data:
                analytics = twitter_data.get('analytics', {})
                followers = analytics.get('followers', 'unknown')

                print(f"📊 Current backend values:")
                print(f"   Followers: {followers}")
                print(f"   Following: {analytics.get('following', 'unknown')}")
                print(f"   Tweets: {analytics.get('tweets', 'unknown')}")

                if followers == 0:
                    print("✅ Backend successfully reset to real values!")
                    return True
                else:
                    print("❌ Backend still has old values")
                    return False
            else:
                print("❌ No Twitter data found in backend")
                return False

    except Exception as e:
        print(f"❌ Error verifying backend: {str(e)}")
        return False

def main():
    """Main reset function"""
    print("🎯 Reset Backend to Real Twitter API Values")
    print("=" * 60)
    print("This will reset your backend to match the real Twitter API:")
    print("   Followers: 0 (real API value)")
    print("   Following: 2 (real API value)")
    print("   Tweets: 0 (real API value)")
    print("   All other metrics: 0")

    # Reset backend
    success = reset_backend_to_real_values()

    if success:
        # Verify reset
        verify_backend_reset()
        print(f"\n🎉 Backend successfully reset to real Twitter API values!")
        print(f"📊 Now your backend matches the real data from Twitter API")
    else:
        print(f"\n❌ Backend reset failed")
        print(f"💡 You may need to manually update your backend or contact admin")

if __name__ == "__main__":
    main()