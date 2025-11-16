#!/usr/bin/env python3
"""
Extract YOUR Real Twitter Data from Twitter API
Uses your credentials to fetch @Presica_Pinto data
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timezone

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class MyTwitterDataExtractor:
    """Extract YOUR real Twitter data using your API credentials"""

    def __init__(self):
        self.bearer_token = None
        self.client_id = None
        self.base_url = "https://api.twitter.com/2"
        self.setup_credentials()

    def setup_credentials(self):
        """Setup YOUR Twitter API credentials"""
        from dotenv import load_dotenv
        load_dotenv()

        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.client_id = os.getenv('TWITTER_CLIENT_ID')

        print(f"✅ YOUR Twitter API credentials loaded:")
        print(f"   Client ID: {self.client_id}")
        print(f"   Bearer Token: {self.bearer_token[:20]}...")

    def get_my_real_data(self, username="Presica_Pinto"):
        """Extract YOUR real data from Twitter API"""
        print(f"\n🐦 Extracting REAL data for @{username} using YOUR API credentials")
        print("=" * 70)

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        # Step 1: Get user data
        print(f"🔍 Step 1: Fetching user data for @{username}")
        user_params = {
            'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
        }

        user_response = requests.get(
            f"{self.base_url}/users/by/username/{username}",
            headers=headers,
            params=user_params
        )

        print(f"   Status: {user_response.status_code}")

        if user_response.status_code == 200:
            user_data = user_response.json()['data']
            public_metrics = user_data.get('public_metrics', {})

            print(f"   ✅ REAL user data obtained:")
            print(f"      Name: {user_data.get('name')}")
            print(f"      Username: @{user_data.get('username')}")
            print(f"      Followers: {public_metrics.get('followers_count', 0):,}")
            print(f"      Following: {public_metrics.get('following_count', 0):,}")
            print(f"      Tweets: {public_metrics.get('tweet_count', 0):,}")
            print(f"      Verified: {user_data.get('verified', False)}")

            # Step 2: Get recent tweets
            print(f"\n📱 Step 2: Fetching recent tweets")
            user_id = user_data.get('id')

            tweet_params = {
                'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
                'max_results': 10,
                'exclude': 'retweets'
            }

            tweet_response = requests.get(
                f"{self.base_url}/users/{user_id}/tweets",
                headers=headers,
                params=tweet_params
            )

            print(f"   Status: {tweet_response.status_code}")

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

                print(f"   ✅ Analyzed {len(tweets)} recent tweets")
                print(f"      Recent Likes: {real_metrics['recent_likes']}")
                print(f"      Recent Retweets: {real_metrics['recent_retweets']}")
                print(f"      Recent Replies: {real_metrics['recent_replies']}")
                print(f"      Recent Impressions: {real_metrics['recent_impressions']}")

            else:
                print(f"   ⚠️ Could not fetch tweets (Status: {tweet_response.status_code})")

            # Step 3: Build YOUR real data JSON
            current_time = datetime.now(timezone.utc).isoformat()

            # Calculate engagement rate
            engagement = 0.0
            if real_metrics['recent_impressions'] > 0:
                total_engagement = (real_metrics['recent_likes'] +
                                  real_metrics['recent_retweets'] +
                                  real_metrics['recent_replies'])
                engagement = round((total_engagement / real_metrics['recent_impressions']) * 100, 2)

            your_real_data = {
                "twitter": {
                    "account_name": user_data.get('username'),
                    "account_type": "user",
                    "analytics": {
                        "data_source": "your_real_api",
                        "engagement": engagement,
                        "followers": public_metrics.get('followers_count', 0),
                        "following": public_metrics.get('following_count', 0),
                        "impressions": real_metrics['recent_impressions'],
                        "likes": real_metrics['recent_likes'],
                        "posts": public_metrics.get('tweet_count', 0),
                        "profile_views": public_metrics.get('profile_views', 0),
                        "quality_score": 0,
                        "reach": public_metrics.get('followers_count', 0),
                        "replies": real_metrics['recent_replies'],
                        "retweets": real_metrics['recent_retweets'],
                        "tweets": public_metrics.get('tweet_count', 0),
                        "verified": user_data.get('verified', False)
                    },
                    "client_id": self.client_id,
                    "connected": True,
                    "created_at": current_time,
                    "last_connected": current_time,
                    "platform": "twitter",
                    "username": user_data.get('username')
                }
            }

            # Save YOUR real data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"MY_REAL_TWITTER_DATA_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(your_real_data, f, indent=2)

            print(f"\n💾 YOUR REAL data saved to: {filename}")

            # Step 4: Compare with backend
            print(f"\n🔍 Step 3: Comparing with your backend data")
            self.compare_with_backend(your_real_data)

            return your_real_data

        else:
            print(f"   ❌ Failed to fetch user data: {user_response.status_code}")
            if user_response.status_code == 429:
                print(f"   ⏰ Rate limit hit - wait 15 minutes")
            elif user_response.status_code == 404:
                print(f"   ❌ User @{username} not found")

            return None

    def compare_with_backend(self, your_real_data):
        """Compare your real API data with backend data"""
        try:
            print(f"📊 Comparing your real API data with backend...")

            # Get backend data
            backend_response = requests.get(
                "http://172.29.89.92:5000/api/social/connections",
                timeout=10
            )

            if backend_response.status_code == 200:
                backend_data = backend_response.json()
                backend_twitter = backend_data.get('connections', {}).get('twitter', {})

                if backend_twitter:
                    backend_analytics = backend_twitter.get('analytics', {})
                    your_analytics = your_real_data['twitter']['analytics']

                    print(f"\n📋 DATA COMPARISON:")
                    print(f"   Metric           Backend (Current)    API (Real)")
                    print(f"   ───────────────────────────────────────────")

                    metrics = ['followers', 'following', 'tweets', 'likes', 'engagement']
                    for metric in metrics:
                        backend_val = backend_analytics.get(metric, 0)
                        api_val = your_analytics.get(metric, 0)
                        print(f"   {metric:<15} {backend_val:<15} {api_val:<15}")

                    # Check if data matches
                    followers_match = backend_analytics.get('followers', 0) == your_analytics.get('followers', 0)
                    print(f"\n   Followers Match: {'✅ YES' if followers_match else '❌ NO'}")

                    if not followers_match:
                        print(f"   💡 Your backend may have outdated data")
                        print(f"   💡 Real API data shows current numbers")

                else:
                    print(f"   ❌ No Twitter data found in backend")

            else:
                print(f"   ❌ Could not fetch backend data: {backend_response.status_code}")

        except Exception as e:
            print(f"   ❌ Error comparing with backend: {str(e)}")

def main():
    """Extract YOUR real Twitter data"""
    print("🐦 YOUR Real Twitter Data Extractor")
    print("=" * 50)
    print("📋 This script extracts YOUR data from Twitter API")
    print("📋 Using YOUR API credentials and YOUR account")

    try:
        extractor = MyTwitterDataExtractor()
        your_real_data = extractor.get_my_real_data("Presica_Pinto")

        if your_real_data:
            print(f"\n🎉 SUCCESS! Your real Twitter data extracted!")
            analytics = your_real_data['twitter']['analytics']
            print(f"✅ Your followers: {analytics['followers']:,}")
            print(f"✅ Your tweets: {analytics['tweets']:,}")
            print(f"✅ Your engagement: {analytics['engagement']:.2f}%")
        else:
            print(f"❌ Failed to extract your real data")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()