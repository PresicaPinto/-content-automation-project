#!/usr/bin/env python3
"""
Clean API Only - ONLY uses Twitter API data
No backend, no fake data, just real API results
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone

def get_real_twitter_data():
    """Get ONLY real Twitter API data"""
    print("🐦 REAL Twitter API Data Only")
    print("=" * 50)
    print("⚠️ ONLY real API data - no backend, no fake data")

    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client_id = os.getenv('TWITTER_CLIENT_ID')

    if not bearer_token or not client_id:
        print("❌ Twitter API credentials missing")
        return None

    print(f"✅ Using API Key: {client_id}")

    # Setup API request
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    # Get user data
    username = "Presica_Pinto"
    print(f"\n🔍 Fetching @{username} from Twitter API...")

    user_url = f"https://api.twitter.com/2/users/by/username/{username}"
    user_params = {
        'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
    }

    try:
        user_response = requests.get(user_url, headers=headers, params=user_params)

        if user_response.status_code == 200:
            user_data = user_response.json()['data']
            public_metrics = user_data.get('public_metrics', {})

            # Get tweets
            user_id = user_data.get('id')
            tweet_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            tweet_params = {
                'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
                'max_results': 10,
                'exclude': 'retweets'
            }

            tweet_response = requests.get(tweet_url, headers=headers, params=tweet_params)

            # Calculate real metrics
            real_metrics = {
                'recent_likes': 0,
                'recent_retweets': 0,
                'recent_replies': 0,
                'recent_impressions': 0,
                'tweets_analyzed': 0
            }

            if tweet_response.status_code == 200:
                tweets = tweet_response.json().get('data', [])
                real_metrics['tweets_analyzed'] = len(tweets)

                for tweet in tweets:
                    tweet_metrics = tweet.get('public_metrics', {})
                    real_metrics['recent_likes'] += tweet_metrics.get('like_count', 0)
                    real_metrics['recent_retweets'] += tweet_metrics.get('retweet_count', 0)
                    real_metrics['recent_replies'] += tweet_metrics.get('reply_count', 0)
                    real_metrics['recent_impressions'] += tweet_metrics.get('impression_count', 0)

            # Build clean JSON
            current_time = datetime.now(timezone.utc).isoformat()

            # Calculate engagement
            engagement = 0.0
            if real_metrics['recent_impressions'] > 0:
                total_engagement = (real_metrics['recent_likes'] +
                                  real_metrics['recent_retweets'] +
                                  real_metrics['recent_replies'])
                engagement = round((total_engagement / real_metrics['recent_impressions']) * 100, 2)

            clean_data = {
                "source": "twitter_api_v2_only",
                "timestamp": current_time,
                "account": {
                    "username": user_data.get('username'),
                    "name": user_data.get('name'),
                    "followers": public_metrics.get('followers_count', 0),
                    "following": public_metrics.get('following_count', 0),
                    "tweets": public_metrics.get('tweet_count', 0),
                    "verified": user_data.get('verified', False),
                    "created_at": user_data.get('created_at'),
                    "description": user_data.get('description'),
                    "profile_image_url": user_data.get('profile_image_url')
                },
                "recent_activity": {
                    "tweets_analyzed": real_metrics['tweets_analyzed'],
                    "recent_likes": real_metrics['recent_likes'],
                    "recent_retweets": real_metrics['recent_retweets'],
                    "recent_replies": real_metrics['recent_replies'],
                    "recent_impressions": real_metrics['recent_impressions'],
                    "engagement_rate": engagement
                },
                "raw_api_response": {
                    "user_data": user_data,
                    "public_metrics": public_metrics,
                    "tweet_metrics": real_metrics
                }
            }

            # Display results
            print(f"\n📊 REAL TWITTER API RESULTS for @{username}:")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Followers: {public_metrics.get('followers_count', 0):,}")
            print(f"   Following: {public_metrics.get('following_count', 0):,}")
            print(f"   Total Tweets: {public_metrics.get('tweet_count', 0):,}")
            print(f"   Verified: {'Yes' if user_data.get('verified') else 'No'}")
            print(f"   Recent Tweets Analyzed: {real_metrics['tweets_analyzed']}")
            print(f"   Recent Likes: {real_metrics['recent_likes']}")
            print(f"   Recent Retweets: {real_metrics['recent_retweets']}")
            print(f"   Recent Replies: {real_metrics['recent_replies']}")
            print(f"   Recent Impressions: {real_metrics['recent_impressions']}")
            print(f"   Engagement Rate: {engagement:.2f}%")

            # Save clean data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"CLEAN_API_DATA_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(clean_data, f, indent=2)

            print(f"\n💾 Clean API data saved to: {filename}")
            print(f"✅ This is 100% real Twitter API data - no backend, no fake data")

            return clean_data

        else:
            print(f"❌ API Error: {user_response.status_code}")
            if user_response.status_code == 429:
                print(f"⏰ Rate limit hit - wait 15 minutes")
            elif user_response.status_code == 404:
                print(f"❌ User @{username} not found")
            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    real_data = get_real_twitter_data()

    if real_data:
        print(f"\n🎉 SUCCESS: Real Twitter API data extracted!")
        print(f"📊 This data comes directly from Twitter's API")
        print(f"🔍 No backend data, no fake data, 100% real")
    else:
        print(f"\n❌ Failed to extract real Twitter API data")