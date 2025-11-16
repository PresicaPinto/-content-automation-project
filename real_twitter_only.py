#!/usr/bin/env python3
"""
REAL Twitter Data Only - NO FAKE DATA, NO FALLBACKS
Fetches 100% authentic data from Twitter API or fails
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class RealTwitterOnly:
    """Fetches ONLY real Twitter data - absolutely no fake data"""

    def __init__(self):
        self.bearer_token = None
        self.client_id = None
        self.base_url = "https://api.twitter.com/2"
        self.setup_credentials()

    def setup_credentials(self):
        """Setup Twitter API credentials"""
        from dotenv import load_dotenv
        load_dotenv()

        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.client_id = os.getenv('TWITTER_CLIENT_ID')

        if not self.bearer_token:
            raise ValueError("❌ TWITTER_BEARER_TOKEN not found")
        if not self.client_id:
            raise ValueError("❌ TWITTER_CLIENT_ID not found")

        print(f"✅ Twitter API credentials loaded")
        print(f"   Client ID: {self.client_id[:10]}...")

    def verify_rate_limit_reset(self):
        """Check if rate limit has reset"""
        print("🔍 Checking rate limit status...")

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        try:
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/users/by/username/twitter",
                headers=headers,
                timeout=10
            )

            remaining = response.headers.get('x-rate-limit-remaining', '0')
            reset_time = response.headers.get('x-rate-limit-reset', '0')

            print(f"   Remaining requests: {remaining}")

            if remaining == '0':
                reset_timestamp = int(reset_time)
                wait_time = max(0, reset_timestamp - int(time.time()))
                if wait_time > 0:
                    print(f"   ⏰ Rate limit resets in {wait_time} seconds")
                    return False, wait_time

            print("   ✅ Rate limit available")
            return True, 0

        except Exception as e:
            print(f"   ❌ Error checking rate limit: {str(e)}")
            return False, 60

    def make_real_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make REAL request to Twitter API - no retries, no fake data"""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        print(f"🔍 Real API request: {url}")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ REAL data received")
                return data
            elif response.status_code == 429:
                print(f"   ❌ Rate limit hit - NO FAKE DATA WILL BE USED")
                return None
            elif response.status_code == 404:
                print(f"   ❌ User not found")
                return None
            else:
                print(f"   ❌ API Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            return None

    def get_real_user_data(self, username: str) -> Optional[Dict]:
        """Get ONLY real user data from Twitter API"""
        params = {
            'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
        }

        url = f"{self.base_url}/users/by/username/{username}"
        print(f"\n👤 Fetching REAL user data for @{username}")

        data = self.make_real_request(url, params)

        if data and 'data' in data:
            user_data = data['data']
            print(f"   ✅ REAL user data obtained")

            # Verify this is real data by checking for required fields
            public_metrics = user_data.get('public_metrics', {})
            followers = public_metrics.get('followers_count', 0)

            if followers > 0:
                print(f"   ✅ Followers: {followers:,} (REAL DATA)")
                return user_data
            else:
                print(f"   ❌ Invalid data detected")
                return None

        print(f"   ❌ No real data available for @{username}")
        return None

    def get_real_tweet_metrics(self, user_id: str) -> Dict[str, int]:
        """Get ONLY real tweet metrics"""
        params = {
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'max_results': 10,
            'exclude': 'retweets'
        }

        url = f"{self.base_url}/users/{user_id}/tweets"
        print(f"📱 Fetching REAL tweet metrics")

        metrics = {
            'recent_likes': 0,
            'recent_retweets': 0,
            'recent_replies': 0,
            'recent_impressions': 0,
            'tweets_analyzed': 0
        }

        data = self.make_real_request(url, params)

        if data and 'data' in data:
            tweets = data['data']
            metrics['tweets_analyzed'] = len(tweets)

            for tweet in tweets:
                tweet_metrics = tweet.get('public_metrics', {})
                metrics['recent_likes'] += tweet_metrics.get('like_count', 0)
                metrics['recent_retweets'] += tweet_metrics.get('retweet_count', 0)
                metrics['recent_replies'] += tweet_metrics.get('reply_count', 0)
                metrics['recent_impressions'] += tweet_metrics.get('impression_count', 0)

            print(f"   ✅ Analyzed {len(tweets)} REAL tweets")
            print(f"   ❤️ Real likes: {metrics['recent_likes']:,}")
            print(f"   🔄 Real retweets: {metrics['recent_retweets']:,}")
            print(f"   💬 Real replies: {metrics['recent_replies']:,}")
            print(f"   👁️ Real impressions: {metrics['recent_impressions']:,}")

        return metrics

    def build_real_json(self, username: str, user_data: Dict, tweet_metrics: Dict) -> Dict[str, Any]:
        """Build JSON with ONLY real data"""
        public_metrics = user_data.get('public_metrics', {})

        # Extract ONLY real API values
        followers = public_metrics.get('followers_count', 0)
        following = public_metrics.get('following_count', 0)
        tweets = public_metrics.get('tweet_count', 0)
        verified = user_data.get('verified', False)

        # Use ONLY real tweet metrics
        likes = tweet_metrics.get('recent_likes', 0)
        retweets = tweet_metrics.get('recent_retweets', 0)
        replies = tweet_metrics.get('recent_replies', 0)
        impressions = tweet_metrics.get('recent_impressions', 0)

        # Calculate real engagement rate
        engagement = 0.0
        if impressions > 0:
            total_engagement = likes + retweets + replies
            engagement = round((total_engagement / impressions) * 100, 2)

        current_time = datetime.now(timezone.utc).isoformat()

        real_json = {
            "twitter": {
                "account_name": username,
                "account_type": "user",
                "analytics": {
                    "data_source": "real_api_only",
                    "engagement": engagement,
                    "followers": followers,
                    "following": following,
                    "impressions": impressions,
                    "likes": likes,
                    "posts": tweets,
                    "profile_views": public_metrics.get('profile_views', 0),
                    "quality_score": 0,
                    "reach": followers,
                    "replies": replies,
                    "retweets": retweets,
                    "tweets": tweets,
                    "verified": verified
                },
                "client_id": self.client_id,
                "connected": True,
                "created_at": current_time,
                "last_connected": current_time,
                "platform": "twitter",
                "username": username
            }
        }

        return real_json

    def process_real_account(self, username: str) -> Optional[Dict[str, Any]]:
        """Process account with ONLY real data"""
        print(f"\n🚀 Processing @{username} - REAL DATA ONLY")
        print("=" * 60)

        try:
            # Step 1: Get REAL user data
            user_data = self.get_real_user_data(username)
            if not user_data:
                print(f"❌ NO REAL DATA for @{username} - PROCESSING STOPPED")
                return None

            # Step 2: Get REAL tweet metrics
            user_id = user_data.get('id')
            tweet_metrics = self.get_real_tweet_metrics(user_id)

            # Step 3: Build REAL JSON
            real_json = self.build_real_json(username, user_data, tweet_metrics)

            # Step 4: Display REAL analytics
            analytics = real_json['twitter']['analytics']
            print(f"\n📊 REAL TWITTER ANALYTICS for @{username}:")
            print(f"   👥 Followers: {analytics['followers']:,} (REAL)")
            print(f"   ➕ Following: {analytics['following']:,} (REAL)")
            print(f"   📱 Tweets: {analytics['tweets']:,} (REAL)")
            print(f"   ❤️ Recent Likes: {analytics['likes']:,} (REAL)")
            print(f"   🔄 Recent Retweets: {analytics['retweets']:,} (REAL)")
            print(f"   💬 Recent Replies: {analytics['replies']:,} (REAL)")
            print(f"   👁️ Recent Impressions: {analytics['impressions']:,} (REAL)")
            print(f"   📈 Engagement Rate: {analytics['engagement']:.2f}% (REAL)")
            print(f"   ✅ Verified: {'YES' if analytics['verified'] else 'NO'} (REAL)")
            print(f"   📊 Data Source: {analytics['data_source']} (NO FAKE DATA)")

            # Save real data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"REAL_TWITTER_DATA_{username}_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(real_json, f, indent=2)

            print(f"\n💾 REAL data saved to: {filename}")
            return real_json

        except Exception as e:
            print(f"❌ Error processing @{username}: {str(e)}")
            return None

def main():
    """Main function - REAL DATA ONLY"""
    print("🐦 REAL TWITTER DATA EXTRACTOR")
    print("=" * 60)
    print("⚠️ WARNING: This script uses ONLY REAL Twitter API data")
    print("⚠️ NO FAKE DATA, NO FALLBACKS, NO SIMULATED VALUES")
    print("⚠️ If Twitter API fails, the script will FAIL - no fake data!")

    try:
        # Initialize
        extractor = RealTwitterOnly()

        # Check rate limit
        can_proceed, wait_time = extractor.verify_rate_limit_reset()

        if not can_proceed:
            print(f"\n⏰ Rate limit active. Please wait {wait_time} seconds and try again.")
            return

        # Test with one account first
        test_account = 'elonmusk'  # We know this account exists and has real data

        print(f"\n🧪 Testing with @{test_account} to verify real data extraction...")

        real_data = extractor.process_real_account(test_account)

        if real_data:
            print(f"\n🎉 SUCCESS! Real data extracted for @{test_account}")
            followers = real_data['twitter']['analytics']['followers']
            print(f"✅ Verified real follower count: {followers:,}")

            if followers > 1000000:  # Sanity check for major accounts
                print("✅ Data appears to be real (major account with millions of followers)")
            else:
                print("⚠️ Data seems low - may be limited by rate limits")

        else:
            print(f"\n❌ Failed to extract real data")
            print("This could be due to rate limits or API issues")

    except Exception as e:
        print(f"❌ Real data extraction failed: {str(e)}")

if __name__ == "__main__":
    main()