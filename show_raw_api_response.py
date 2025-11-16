#!/usr/bin/env python3
"""
Show Raw API Response - Proves numbers are not hardcoded
"""

import os
import requests
import json
from dotenv import load_dotenv

def show_raw_response():
    """Show the exact raw response from Twitter API"""
    print("🔍 RAW TWITTER API RESPONSE")
    print("=" * 50)
    print("This shows the EXACT response from Twitter API")
    print("No hardcoded numbers - pure API data!")

    load_dotenv()
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("❌ Bearer Token not found")
        return

    headers = {'Authorization': f'Bearer {bearer_token}'}
    params = {'user.fields': 'public_metrics,verified,description,created_at'}

    print(f"\n📡 Making API Call:")
    print(f"   URL: https://api.twitter.com/2/users/by/username/Presica_Pinto")
    print(f"   Headers: Authorization: Bearer {bearer_token[:20]}...")
    print(f"   Params: {params}")

    try:
        response = requests.get(
            'https://api.twitter.com/2/users/by/username/Presica_Pinto',
            headers=headers,
            params=params
        )

        print(f"\n📊 API Response Status: {response.status_code}")

        if response.status_code == 200:
            print(f"\n✅ SUCCESS! Raw API Response:")
            print("=" * 60)

            raw_data = response.json()
            print(json.dumps(raw_data, indent=2))

            print(f"\n" + "=" * 60)
            print(f"🔍 WHERE DO THE NUMBERS COME FROM?")
            print("=" * 60)

            if 'data' in raw_data:
                user_data = raw_data['data']
                public_metrics = user_data.get('public_metrics', {})

                print(f"📋 EXTRACTED FROM API RESPONSE:")
                print(f"   followers: {public_metrics.get('followers_count', 0)}")
                print(f"   following: {public_metrics.get('following_count', 0)}")
                print(f"   tweets: {public_metrics.get('tweet_count', 0)}")
                print(f"   verified: {user_data.get('verified', False)}")

                print(f"\n🔍 PROOF THESE ARE NOT HARDCODED:")
                print(f"   ✅ followers comes from: public_metrics.followers_count")
                print(f"   ✅ following comes from: public_metrics.following_count")
                print(f"   ✅ tweets comes from: public_metrics.tweet_count")
                print(f"   ✅ All values extracted from: response.json()['data']['public_metrics']")

                print(f"\n💡 IF YOUR ACCOUNT CHANGES:")
                print(f"   📱 If you get followers: API will return new number")
                print(f"   📱 If you post tweets: API will return new count")
                print(f"   📱 If you follow people: API will return new count")
                print(f"   📱 These are LIVE values from Twitter's servers!")

        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🎯 PROOF: Numbers are NOT hardcoded!")
    print("=" * 60)
    print("This will show the raw API response")
    print("You'll see exactly where the numbers come from")

    show_raw_response()

if __name__ == "__main__":
    main()