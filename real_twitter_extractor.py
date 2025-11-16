#!/usr/bin/env python3
"""
Real Twitter Data Extractor - Ensures actual API data extraction
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class RealTwitterExtractor:
    """Direct Twitter API client for guaranteed real data extraction"""

    def __init__(self):
        self.bearer_token = None
        self.base_url = "https://api.twitter.com/2"
        self.setup_credentials()

    def setup_credentials(self):
        """Setup Twitter API credentials"""
        from dotenv import load_dotenv
        load_dotenv()

        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not self.bearer_token:
            print("❌ Bearer Token not found in environment variables")
            return False

        print(f"✅ Bearer Token loaded: {self.bearer_token[:20]}...")
        return True

    def get_user_by_username(self, username):
        """Get user data directly from Twitter API v2"""
        if not self.bearer_token:
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }

            params = {
                'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
            }

            url = f"{self.base_url}/users/by/username/{username}"
            print(f"🔍 Fetching from: {url}")

            response = requests.get(url, headers=headers, params=params)

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Real API data received for @{username}")
                return data
            elif response.status_code == 429:
                print(f"   ⚠️ Rate limit hit for @{username}")
                return None
            elif response.status_code == 404:
                print(f"   ❌ User @{username} not found")
                return None
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return None

    def get_user_tweets(self, user_id, max_results=10):
        """Get user tweets directly from Twitter API v2"""
        if not self.bearer_token:
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }

            params = {
                'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
                'max_results': max_results,
                'exclude': 'retweets'
            }

            url = f"{self.base_url}/users/{user_id}/tweets"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Tweet API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"   Tweet fetch error: {str(e)}")
            return None

    def extract_real_data(self, usernames):
        """Extract only real data from Twitter API"""
        print("🐦 Real Twitter Data Extractor")
        print("=" * 60)
        print("🚀 Extracting ONLY real Twitter API data...")

        if not self.bearer_token:
            print("❌ Cannot proceed without Bearer Token")
            return {}

        real_data = {}

        for username in usernames:
            print(f"\n🔍 Extracting data for @{username}...")

            # Get user data
            user_response = self.get_user_by_username(username)

            if user_response and 'data' in user_response:
                user_data = user_response['data']

                # Extract real metrics
                public_metrics = user_data.get('public_metrics', {})

                analytics = {
                    'username': username,
                    'user_id': user_data.get('id'),
                    'name': user_data.get('name'),
                    'followers': public_metrics.get('followers_count', 0),
                    'following': public_metrics.get('following_count', 0),
                    'tweets': public_metrics.get('tweet_count', 0),
                    'verified': user_data.get('verified', False),
                    'created_at': user_data.get('created_at'),
                    'description': user_data.get('description'),
                    'profile_image_url': user_data.get('profile_image_url'),
                    'data_source': 'real_api',
                    'extraction_timestamp': datetime.now().isoformat()
                }

                # Get recent tweets for engagement data
                tweets_response = self.get_user_tweets(user_data.get('id'), max_results=5)

                if tweets_response and 'data' in tweets_response:
                    tweets = tweets_response['data']
                    total_likes = 0
                    total_retweets = 0
                    total_replies = 0
                    total_impressions = 0

                    for tweet in tweets:
                        metrics = tweet.get('public_metrics', {})
                        total_likes += metrics.get('like_count', 0)
                        total_retweets += metrics.get('retweet_count', 0)
                        total_replies += metrics.get('reply_count', 0)
                        total_impressions += metrics.get('impression_count', 0)

                    analytics.update({
                        'recent_tweets_count': len(tweets),
                        'recent_likes': total_likes,
                        'recent_retweets': total_retweets,
                        'recent_replies': total_replies,
                        'recent_impressions': total_impressions,
                    })

                    # Calculate engagement rate
                    if total_impressions > 0:
                        engagement = total_likes + total_retweets + total_replies
                        analytics['engagement_rate'] = round((engagement / total_impressions) * 100, 2)
                    else:
                        analytics['engagement_rate'] = 0

                real_data[username] = analytics

                # Display real data
                print(f"   ✅ REAL DATA for @{username}:")
                print(f"      Name: {user_data.get('name')}")
                print(f"      Followers: {analytics['followers']:,}")
                print(f"      Following: {analytics['following']:,}")
                print(f"      Total Tweets: {analytics['tweets']:,}")
                print(f"      Verified: {'✓' if analytics['verified'] else '✗'}")

                if 'engagement_rate' in analytics:
                    print(f"      Recent Engagement: {analytics['engagement_rate']:.2f}%")
                    print(f"      Recent Tweets Analyzed: {analytics['recent_tweets_count']}")

            else:
                print(f"   ❌ Failed to get real data for @{username}")
                print(f"   (Will not include fallback data - only real API results)")

        return real_data

    def save_real_data(self, data, filename_suffix=None):
        """Save real data to file"""
        if not data:
            print("❌ No real data to save")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        suffix = f"_{filename_suffix}" if filename_suffix else ""
        filename = f"real_twitter_data_{timestamp}{suffix}.json"

        # Add metadata
        output_data = {
            'extraction_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_accounts': len(data),
                'data_source': 'twitter_api_v2_only',
                'no_fallback_data': True,
                'auth_method': 'bearer_token'
            },
            'real_data': data
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Real data saved to: {filename}")
        return filename

def main():
    """Main function to extract real Twitter data"""
    extractor = RealTwitterExtractor()

    if not extractor.bearer_token:
        print("❌ Cannot proceed without Bearer Token")
        return

    # Test with known accounts
    test_usernames = [
        'elonmusk',
        'nasa',
        'twitter',
        'github',
        'realDonaldTrump'
    ]

    # Extract only real data
    real_data = extractor.extract_real_data(test_usernames)

    # Save results
    if real_data:
        filename = extractor.save_real_data(real_data)

        print(f"\n📋 REAL DATA SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully extracted REAL data for {len(real_data)} accounts")

        total_followers = sum(data['followers'] for data in real_data.values())
        total_tweets = sum(data['tweets'] for data in real_data.values())

        print(f"📊 Total Followers: {total_followers:,}")
        print(f"📱 Total Tweets: {total_tweets:,}")
        print(f"💾 Data saved to: {filename}")

        # Display account details
        print(f"\n📋 Account Details:")
        for username, data in real_data.items():
            print(f"   @{username}: {data['followers']:,} followers ({data['tweets']:,} tweets)")

        print(f"\n🎉 Successfully extracted REAL Twitter data!")
        print("✅ No fallback or simulated data included")

    else:
        print("❌ No real data was extracted")
        print("This could be due to:")
        print("   • Rate limiting (too many requests)")
        print("   • Invalid Bearer Token")
        print("   • Network issues")
        print("   • Twitter API issues")

if __name__ == "__main__":
    main()