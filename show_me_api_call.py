#!/usr/bin/env python3
"""
Show Me The API Call - Transparent Twitter API request
Shows exactly what URL is called and what response is received
"""

import os
import sys
import requests
import json

def show_exact_api_call():
    """Show the exact API call and response"""
    print("🔍 SHOWING EXACT TWITTER API CALL")
    print("=" * 60)

    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client_id = os.getenv('TWITTER_CLIENT_ID')

    print(f"📋 Using Credentials:")
    print(f"   Client ID: {client_id}")
    print(f"   Bearer Token: {bearer_token[:20]}...{bearer_token[-10:]}")

    # Build the exact API request
    username = "Presica_Pinto"
    api_url = f"https://api.twitter.com/2/users/by/username/{username}"

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    params = {
        'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
    }

    print(f"\n📡 EXACT API REQUEST:")
    print(f"   Method: GET")
    print(f"   URL: {api_url}")
    print(f"   Headers: {json.dumps(headers, indent=6)}")
    print(f"   Params: {json.dumps(params, indent=6)}")

    print(f"\n🔄 MAKING THE API CALL...")

    try:
        response = requests.get(api_url, headers=headers, params=params)

        print(f"\n📊 API RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers:")
        for key, value in response.headers.items():
            print(f"      {key}: {value}")

        if response.status_code == 200:
            print(f"\n✅ SUCCESS - Raw Response Body:")
            response_data = response.json()
            print(json.dumps(response_data, indent=3))

            # Extract the specific values
            if 'data' in response_data:
                user_data = response_data['data']
                public_metrics = user_data.get('public_metrics', {})

                print(f"\n📋 EXTRACTED VALUES:")
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Name: {user_data.get('name')}")
                print(f"   Username: {user_data.get('username')}")
                print(f"   Followers: {public_metrics.get('followers_count', 'NOT_FOUND')}")
                print(f"   Following: {public_metrics.get('following_count', 'NOT_FOUND')}")
                print(f"   Tweets: {public_metrics.get('tweet_count', 'NOT_FOUND')}")
                print(f"   Verified: {user_data.get('verified', 'NOT_FOUND')}")
                print(f"   Created: {user_data.get('created_at', 'NOT_FOUND')}")

                print(f"\n🎯 CONCLUSION:")
                print(f"   These values come directly from Twitter's API")
                print(f"   No searching, no estimates, no fake data")
                print(f"   Just the raw API response to your authenticated request")

        else:
            print(f"\n❌ API ERROR:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

            if response.status_code == 429:
                print(f"   Rate limit hit - Twitter says 'too many requests'")
            elif response.status_code == 401:
                print(f"   Authentication failed - check your Bearer Token")
            elif response.status_code == 403:
                print(f"   Forbidden - API access issue")
            elif response.status_code == 404:
                print(f"   User @{username} not found on Twitter")

    except Exception as e:
        print(f"❌ REQUEST FAILED: {str(e)}")

def main():
    print("🐦 TRANSPARENT TWITTER API CALL DEMO")
    print("=" * 60)
    print("This script shows you EXACTLY what happens when we call Twitter API")
    print("No magic, no hiding - just transparent API calls")

    show_exact_api_call()

if __name__ == "__main__":
    main()