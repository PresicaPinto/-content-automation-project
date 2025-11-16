#!/usr/bin/env python3
"""
Twitter API Integration for Backend Analytics
Fetches real Twitter data and sends to backend endpoint
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

class TwitterBackendIntegration:
    """Integrates Twitter API with backend analytics endpoint"""

    def __init__(self):
        self.bearer_token = None
        self.client_id = None
        self.base_url = "https://api.twitter.com/2"
        self.backend_endpoint = "http://172.29.89.92:5000/api/social/connections"
        self.setup_credentials()

    def setup_credentials(self):
        """Setup Twitter API credentials"""
        from dotenv import load_dotenv
        load_dotenv()

        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.client_id = os.getenv('TWITTER_CLIENT_ID')

        if not self.bearer_token:
            raise ValueError("❌ TWITTER_BEARER_TOKEN not found in environment variables")
        if not self.client_id:
            raise ValueError("❌ TWITTER_CLIENT_ID not found in environment variables")

        print(f"✅ Twitter API credentials loaded")
        print(f"   Client ID: {self.client_id[:10]}...")
        print(f"   Bearer Token: {self.bearer_token[:20]}...")

    def make_twitter_request(self, url: str, params: Dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """Make authenticated request to Twitter API with retry logic"""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        for attempt in range(max_retries):
            try:
                # Rate limiting: wait between requests
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    time.sleep(1)  # Base delay

                response = requests.get(url, headers=headers, params=params)

                # Check rate limits
                remaining = response.headers.get('x-rate-limit-remaining', 'unknown')
                if remaining != 'unknown' and int(remaining) < 5:
                    print(f"⚠️ Rate limit warning: {remaining} requests remaining")

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limit hit - wait for reset
                    reset_time = response.headers.get('x-rate-limit-reset')
                    if reset_time:
                        wait_time = max(0, int(reset_time) - int(time.time()))
                        print(f"⏰ Rate limit hit. Waiting {wait_time} seconds...")
                        time.sleep(wait_time + 5)
                        continue
                    else:
                        print("⏰ Rate limit hit. Waiting 60 seconds...")
                        time.sleep(60)
                        continue
                else:
                    print(f"❌ Twitter API error {response.status_code}: {response.text}")
                    if attempt == max_retries - 1:
                        return None
                    continue

            except Exception as e:
                print(f"❌ Request error (attempt {attempt + 1}): {str(e)}")
                if attempt == max_retries - 1:
                    return None

        return None

    def get_user_data(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch user data from Twitter API v2"""
        params = {
            'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
        }

        url = f"{self.base_url}/users/by/username/{username}"
        print(f"🔍 Fetching user data for @{username}...")

        response = self.make_twitter_request(url, params)
        if response and response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print(f"✅ Successfully fetched user data for @{username}")
                return data['data']

        print(f"❌ Failed to fetch user data for @{username}")
        return None

    def get_user_tweets_metrics(self, user_id: str, max_results: int = 10) -> Dict[str, int]:
        """Fetch recent tweets and calculate engagement metrics"""
        params = {
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang',
            'max_results': min(max_results, 100),
            'exclude': 'retweets'
        }

        url = f"{self.base_url}/users/{user_id}/tweets"
        print(f"🔍 Fetching tweet metrics for user {user_id}...")

        response = self.make_twitter_request(url, params)

        metrics = {
            'recent_likes': 0,
            'recent_retweets': 0,
            'recent_replies': 0,
            'recent_impressions': 0,
            'recent_quotes': 0,
            'tweets_analyzed': 0
        }

        if response and response.status_code == 200:
            data = response.json()
            if 'data' in data:
                tweets = data['data']
                metrics['tweets_analyzed'] = len(tweets)

                for tweet in tweets:
                    tweet_metrics = tweet.get('public_metrics', {})
                    metrics['recent_likes'] += tweet_metrics.get('like_count', 0)
                    metrics['recent_retweets'] += tweet_metrics.get('retweet_count', 0)
                    metrics['recent_replies'] += tweet_metrics.get('reply_count', 0)
                    metrics['recent_impressions'] += tweet_metrics.get('impression_count', 0)
                    metrics['recent_quotes'] += tweet_metrics.get('quote_count', 0)

                print(f"✅ Analyzed {len(tweets)} recent tweets")

        return metrics

    def calculate_engagement_rate(self, likes: int, retweets: int, replies: int, impressions: int) -> float:
        """Calculate engagement rate as percentage"""
        if impressions == 0:
            return 0.0

        total_engagement = likes + retweets + replies
        return round((total_engagement / impressions) * 100, 2)

    def build_analytics_json(self, username: str, user_data: Dict, tweet_metrics: Dict) -> Dict[str, Any]:
        """Build the required JSON structure for backend"""
        public_metrics = user_data.get('public_metrics', {})

        # Extract real API values
        followers = public_metrics.get('followers_count', 0)
        following = public_metrics.get('following_count', 0)
        tweets = public_metrics.get('tweet_count', 0)

        # Use recent tweet metrics if available, otherwise use user profile metrics
        likes = tweet_metrics.get('recent_likes', 0)
        retweets = tweet_metrics.get('recent_retweets', 0)
        replies = tweet_metrics.get('recent_replies', 0)
        impressions = tweet_metrics.get('recent_impressions', 0)

        # Calculate engagement rate
        engagement = self.calculate_engagement_rate(likes, retweets, replies, impressions)

        # Get current timestamp
        current_time = datetime.now(timezone.utc).isoformat()

        analytics_json = {
            "twitter": {
                "account_name": username,
                "account_type": "user",
                "analytics": {
                    "data_source": "api",
                    "engagement": engagement,
                    "followers": followers,
                    "following": following,
                    "impressions": impressions,
                    "likes": likes,
                    "posts": tweets,
                    "profile_views": public_metrics.get('profile_views', 0),
                    "quality_score": 0,  # Default value as specified
                    "reach": followers,  # Using followers as reach metric
                    "replies": replies,
                    "retweets": retweets,
                    "tweets": tweets,
                    "verified": user_data.get('verified', False)
                },
                "client_id": self.client_id,
                "connected": True,
                "created_at": current_time,
                "last_connected": current_time,
                "platform": "twitter",
                "username": username
            }
        }

        return analytics_json

    def send_to_backend(self, analytics_data: Dict[str, Any]) -> bool:
        """Send analytics data to backend endpoint"""
        print(f"📤 Sending analytics to backend: {self.backend_endpoint}")

        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'TwitterAnalyticsIntegration/1.0'
            }

            response = requests.post(
                self.backend_endpoint,
                json=analytics_data,
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 201, 204]:
                print(f"✅ Successfully sent analytics to backend")
                return True
            else:
                print(f"❌ Backend error {response.status_code}: {response.text}")
                return False

        except requests.exceptions.Timeout:
            print(f"❌ Backend request timeout")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend endpoint")
            return False
        except Exception as e:
            print(f"❌ Backend request error: {str(e)}")
            return False

    def process_account(self, username: str) -> bool:
        """Process a single Twitter account and send to backend"""
        print(f"\n🚀 Processing Twitter account: @{username}")
        print("=" * 60)

        try:
            # Step 1: Get user data
            user_data = self.get_user_data(username)
            if not user_data:
                print(f"❌ Failed to get user data for @{username}")
                return False

            # Step 2: Get tweet metrics
            user_id = user_data.get('id')
            tweet_metrics = self.get_user_tweets_metrics(user_id)

            # Step 3: Build analytics JSON
            analytics_json = self.build_analytics_json(username, user_data, tweet_metrics)

            # Step 4: Display summary
            analytics = analytics_json['twitter']['analytics']
            print(f"\n📊 Analytics Summary for @{username}:")
            print(f"   Followers: {analytics['followers']:,}")
            print(f"   Following: {analytics['following']:,}")
            print(f"   Tweets: {analytics['tweets']:,}")
            print(f"   Recent Likes: {analytics['likes']:,}")
            print(f"   Recent Retweets: {analytics['retweets']:,}")
            print(f"   Recent Replies: {analytics['replies']:,}")
            print(f"   Recent Impressions: {analytics['impressions']:,}")
            print(f"   Engagement Rate: {analytics['engagement']:.2f}%")
            print(f"   Verified: {'✓' if analytics['verified'] else '✗'}")

            # Step 5: Send to backend
            success = self.send_to_backend(analytics_json)
            if success:
                print(f"✅ Analytics for @{username} successfully stored in backend")
            else:
                print(f"❌ Failed to store analytics for @{username} in backend")

            return success

        except Exception as e:
            print(f"❌ Error processing @{username}: {str(e)}")
            return False

    def process_multiple_accounts(self, usernames: list, delay_between_accounts: int = 60):
        """Process multiple Twitter accounts with delays"""
        print(f"🐦 Twitter Backend Integration")
        print("=" * 60)
        print(f"📊 Processing {len(usernames)} accounts")
        print(f"🏁 Backend Endpoint: {self.backend_endpoint}")
        print(f"⏰ Delay between accounts: {delay_between_accounts} seconds")

        results = {}

        for i, username in enumerate(usernames, 1):
            print(f"\n📍 Account {i}/{len(usernames)}: @{username}")
            print("-" * 40)

            success = self.process_account(username)
            results[username] = success

            # Add delay between accounts (except for the last one)
            if i < len(usernames):
                print(f"\n⏳ Waiting {delay_between_accounts} seconds before next account...")
                time.sleep(delay_between_accounts)

        # Summary
        print(f"\n📋 PROCESSING SUMMARY")
        print("=" * 60)
        successful = sum(1 for success in results.values() if success)
        total = len(results)

        print(f"✅ Successfully processed: {successful}/{total} accounts")
        print(f"❌ Failed: {total - successful}/{total} accounts")

        for username, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"   @{username}: {status}")

        return results

def main():
    """Main function"""
    try:
        # Initialize integration
        integration = TwitterBackendIntegration()

        # Define accounts to process
        target_accounts = [
            'elonmusk',
            'nasa',
            'twitter'
        ]

        # Process all accounts
        results = integration.process_multiple_accounts(
            target_accounts,
            delay_between_accounts=30  # 30 seconds between accounts
        )

        print(f"\n🎉 Twitter to Backend integration completed!")

    except Exception as e:
        print(f"❌ Integration failed: {str(e)}")

if __name__ == "__main__":
    main()