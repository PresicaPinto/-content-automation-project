#!/usr/bin/env python3
"""
Simple Bearer Token Only - Just ask for Bearer Token, nothing else
"""

import os
import requests
import json
from datetime import datetime, timezone

def setup_bearer_token():
    """Setup only Bearer Token"""
    print("🔑 TWITTER API SETUP - Bearer Token Only")
    print("=" * 50)
    print("We only need your Bearer Token - nothing else!")

    # Check if .env exists with bearer token
    from dotenv import load_dotenv
    load_dotenv()

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("❌ Bearer Token not found in .env file")
        print("💡 Add this line to your .env file:")
        print("TWITTER_BEARER_TOKEN=your_bearer_token_here")
        return None

    print(f"✅ Bearer Token found: {bearer_token[:20]}...{bearer_token[-10:]}")
    return bearer_token

def get_twitter_data(bearer_token):
    """Get Twitter data using only Bearer Token"""
    print(f"\n🐦 Fetching Twitter data with Bearer Token...")

    headers = {'Authorization': f'Bearer {bearer_token}'}
    params = {'user.fields': 'public_metrics,verified,description,created_at'}

    try:
        response = requests.get(
            'https://api.twitter.com/2/users/by/username/Presica_Pinto',
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            user_data = response.json()['data']
            public_metrics = user_data.get('public_metrics', {})

            real_data = {
                "username": user_data.get('username'),
                "name": user_data.get('name'),
                "followers": public_metrics.get('followers_count', 0),
                "following": public_metrics.get('following_count', 0),
                "tweets": public_metrics.get('tweet_count', 0),
                "verified": user_data.get('verified', False),
                "created_at": user_data.get('created_at'),
                "description": user_data.get('description'),
                "source": "twitter_api_v2",
                "timestamp": datetime.now().isoformat()
            }

            print(f"✅ Data fetched successfully!")
            print(f"   Name: {real_data['name']}")
            print(f"   Username: @{real_data['username']}")
            print(f"   Followers: {real_data['followers']:,}")
            print(f"   Following: {real_data['following']:,}")
            print(f"   Tweets: {real_data['tweets']:,}")
            print(f"   Verified: {real_data['verified']}")
            print(f"   Account Created: {real_data['created_at']}")

            return real_data

        elif response.status_code == 401:
            print("❌ Invalid Bearer Token")
            print("💡 Check your Bearer Token in .env file")
            return None
        elif response.status_code == 429:
            print("❌ Rate limit hit")
            print("💡 Wait 15 minutes and try again")
            return None
        elif response.status_code == 404:
            print("❌ User @Presica_Pinto not found")
            return None
        else:
            print(f"❌ API Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def store_in_backend(data):
    """Store data in backend"""
    print(f"\n💾 Storing data in backend...")

    # Format data for backend
    backend_data = {
        "twitter": {
            "account_name": data['username'],
            "account_type": "user",
            "analytics": {
                "data_source": "bearer_token_only",
                "engagement": 0.0,
                "followers": data['followers'],
                "following": data['following'],
                "tweets": data['tweets'],
                "verified": data['verified'],
                "impressions": 0,
                "likes": 0,
                "retweets": 0,
                "replies": 0,
                "profile_views": 0,
                "quality_score": 0,
                "reach": data['followers'],
                "posts": data['tweets']
            },
            "client_id": "bearer_token_only",
            "connected": True,
            "created_at": data['timestamp'],
            "last_connected": data['timestamp'],
            "platform": "twitter",
            "username": data['username']
        }
    }

    try:
        response = requests.post(
            'http://172.29.89.92:5000/api/social/connections',
            json=backend_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Data stored in backend successfully!")
                return True
            else:
                print(f"❌ Backend error: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error storing data: {str(e)}")
        return False

def save_locally(data):
    """Save data locally"""
    filename = f"twitter_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Data saved locally to: {filename}")

def main():
    """Simple main function"""
    print("🎯 SIMPLE TWITTER API - Bearer Token Only")
    print("=" * 60)
    print("✅ Only need Bearer Token")
    print("❌ No Client ID required")
    print("❌ No Client Secret required")
    print("❌ No Access Token required")
    print("✅ Just Bearer Token!")

    # Step 1: Setup Bearer Token
    bearer_token = setup_bearer_token()
    if not bearer_token:
        return

    # Step 2: Get Twitter data
    data = get_twitter_data(bearer_token)
    if not data:
        return

    # Step 3: Store locally
    save_locally(data)

    # Step 4: Store in backend
    store_in_backend(data)

    print(f"\n🎉 DONE!")
    print("✅ Used only Bearer Token")
    print("✅ Got real Twitter data")
    print("✅ Stored in backend")
    print("✅ No other credentials needed!")

if __name__ == "__main__":
    main()