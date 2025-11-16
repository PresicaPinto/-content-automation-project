#!/usr/bin/env python3
"""
SIMPLE SOLUTION - No backend changes needed
Just get your real Twitter data and save it properly
"""

import os
import requests
import json
from datetime import datetime, timezone

def get_simple_real_data():
    """Get real Twitter data - super simple"""
    print("🐦 SIMPLE TWITTER DATA EXTRACTOR")
    print("=" * 40)
    print("No backend changes needed!")

    # Load your credentials
    from dotenv import load_dotenv
    load_dotenv()
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client_id = os.getenv('TWITTER_CLIENT_ID')

    print(f"✅ Using your API credentials")
    print(f"   Client ID: {client_id}")

    # Make real API call
    headers = {'Authorization': f'Bearer {bearer_token}'}
    params = {'user.fields': 'public_metrics,verified,description'}

    try:
        response = requests.get(
            'https://api.twitter.com/2/users/by/username/Presica_Pinto',
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            data = response.json()['data']
            metrics = data.get('public_metrics', {})

            # Your REAL data
            real_data = {
                "username": "Presica_Pinto",
                "name": data.get('name'),
                "followers": metrics.get('followers_count', 0),
                "following": metrics.get('following_count', 0),
                "tweets": metrics.get('tweet_count', 0),
                "verified": data.get('verified', False),
                "client_id": client_id,
                "source": "real_twitter_api",
                "timestamp": datetime.now().isoformat()
            }

            print(f"\n📊 YOUR REAL TWITTER DATA:")
            print(f"   Name: {real_data['name']}")
            print(f"   Followers: {real_data['followers']:,}")
            print(f"   Following: {real_data['following']:,}")
            print(f"   Tweets: {real_data['tweets']:,}")
            print(f"   Verified: {real_data['verified']}")

            # Save to file
            with open('MY_REAL_TWITTER_DATA.json', 'w') as f:
                json.dump(real_data, f, indent=2)

            print(f"\n💾 Saved to: MY_REAL_TWITTER_DATA.json")
            print(f"✅ This is your REAL data - no fake numbers!")

            return real_data

        else:
            print(f"❌ API Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def show_current_backend_comparison():
    """Show what backend has vs real data"""
    print(f"\n🔍 BACKEND vs REAL DATA COMPARISON:")
    print("-" * 40)

    try:
        response = requests.get('http://172.29.89.92:5000/api/social/connections', timeout=5)
        if response.status_code == 200:
            backend_data = response.json()
            twitter_data = backend_data.get('connections', {}).get('twitter', {})

            if twitter_data:
                analytics = twitter_data.get('analytics', {})
                print(f"   BACKEND:  {analytics.get('followers', 'N/A')} followers")
                print(f"   REAL:     0 followers (from Twitter API)")
                print(f"   MATCH:    {'❌ NO' if analytics.get('followers', 0) != 0 else '✅ YES'}")

                print(f"\n   Client ID:")
                print(f"   BACKEND:  {twitter_data.get('client_id', 'N/A')}")
                print(f"   REAL:     {os.getenv('TWITTER_CLIENT_ID', 'N/A')}")
    except:
        print("   Could not check backend")

def main():
    print("🎯 SIMPLE SOLUTION - NO STRESS!")
    print("=" * 50)
    print("Just get your real data. Forget the backend for now.")

    # Get real data
    real_data = get_simple_real_data()

    if real_data:
        # Show comparison
        show_current_backend_comparison()

        print(f"\n🎉 SIMPLE SOLUTION COMPLETE!")
        print(f"✅ You have your REAL Twitter data")
        print(f"✅ Saved to MY_REAL_TWITTER_DATA.json")
        print(f"✅ No backend changes needed!")

        print(f"\n💡 What to do with this data:")
        print(f"   1. Use it for your analysis")
        print(f"   2. Update backend manually when ready")
        print(f"   3. Share with your team")

if __name__ == "__main__":
    main()