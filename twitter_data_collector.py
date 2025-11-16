#!/usr/bin/env python3
"""
Twitter Data Collector - Fetches live Twitter analytics and stores in backend-compatible format
Perfect for syncing with your backend at http://172.29.89.92:5000/api/social/connections
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TwitterDataCollector:
    """Fetches real Twitter data in backend-compatible format"""

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

    def make_twitter_request(self, url: str, params: Dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """Make authenticated request to Twitter API with rate limit protection"""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        for attempt in range(max_retries):
            try:
                # Rate limiting: smart delays
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
                    # Handle rate limit
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

    def build_backend_json(self, username: str, user_data: Dict, tweet_metrics: Dict) -> Dict[str, Any]:
        """Build the exact JSON structure your backend expects"""
        public_metrics = user_data.get('public_metrics', {})

        # Extract real API values
        followers = public_metrics.get('followers_count', 0)
        following = public_metrics.get('following_count', 0)
        tweets = public_metrics.get('tweet_count', 0)

        # Use recent tweet metrics if available
        likes = tweet_metrics.get('recent_likes', 0)
        retweets = tweet_metrics.get('recent_retweets', 0)
        replies = tweet_metrics.get('recent_replies', 0)
        impressions = tweet_metrics.get('recent_impressions', 0)

        # Calculate engagement rate
        engagement = self.calculate_engagement_rate(likes, retweets, replies, impressions)

        # Get current timestamp
        current_time = datetime.now(timezone.utc).isoformat()

        # Build exact backend-compatible JSON
        backend_json = {
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
                    "quality_score": 0,
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

        return backend_json

    def save_data_locally(self, username: str, data: Dict[str, Any]) -> str:
        """Save data locally in backend-compatible format"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"twitter_data_{username}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Data saved locally to: {filename}")
        return filename

    def compare_with_backend(self, username: str, new_data: Dict[str, Any]) -> bool:
        """Compare new data with existing backend data"""
        try:
            print(f"🔍 Comparing new data with backend for @{username}...")

            # Get current backend data
            response = requests.get(self.backend_endpoint, timeout=10)
            if response.status_code == 200:
                backend_data = response.json()

                # Extract existing Twitter data
                existing_twitter = backend_data.get('connections', {}).get('twitter', {})

                if existing_twitter and existing_twitter.get('username') == username:
                    existing_analytics = existing_twitter.get('analytics', {})
                    new_analytics = new_data['twitter']['analytics']

                    # Compare key metrics
                    metrics_to_compare = ['followers', 'following', 'tweets', 'likes', 'engagement']

                    print(f"📊 Data Comparison for @{username}:")
                    for metric in metrics_to_compare:
                        old_val = existing_analytics.get(metric, 0)
                        new_val = new_analytics.get(metric, 0)
                        change = new_val - old_val
                        change_str = f"+{change}" if change > 0 else str(change)
                        print(f"   {metric}: {old_val:,} → {new_val:,} ({change_str})")

                    return True
                else:
                    print(f"ℹ️ No existing data found for @{username} in backend")
                    return False
            else:
                print(f"⚠️ Could not fetch backend data for comparison")
                return False

        except Exception as e:
            print(f"❌ Error comparing with backend: {str(e)}")
            return False

    def process_account(self, username: str, save_locally: bool = True, compare_with_backend: bool = True) -> Optional[Dict[str, Any]]:
        """Process a single Twitter account"""
        print(f"\n🚀 Processing Twitter account: @{username}")
        print("=" * 60)

        try:
            # Step 1: Get user data
            user_data = self.get_user_data(username)
            if not user_data:
                print(f"❌ Failed to get user data for @{username}")
                return None

            # Step 2: Get tweet metrics
            user_id = user_data.get('id')
            tweet_metrics = self.get_user_tweets_metrics(user_id)

            # Step 3: Build backend-compatible JSON
            backend_json = self.build_backend_json(username, user_data, tweet_metrics)

            # Step 4: Display analytics summary
            analytics = backend_json['twitter']['analytics']
            print(f"\n📊 Real Twitter Analytics for @{username}:")
            print(f"   Followers: {analytics['followers']:,}")
            print(f"   Following: {analytics['following']:,}")
            print(f"   Tweets: {analytics['tweets']:,}")
            print(f"   Recent Likes: {analytics['likes']:,}")
            print(f"   Recent Retweets: {analytics['retweets']:,}")
            print(f"   Recent Replies: {analytics['replies']:,}")
            print(f"   Recent Impressions: {analytics['impressions']:,}")
            print(f"   Engagement Rate: {analytics['engagement']:.2f}%")
            print(f"   Verified: {'✓' if analytics['verified'] else '✗'}")
            print(f"   Data Source: {analytics['data_source']}")

            # Step 5: Compare with backend (if requested)
            if compare_with_backend:
                self.compare_with_backend(username, backend_json)

            # Step 6: Save locally (if requested)
            if save_locally:
                filename = self.save_data_locally(username, backend_json)
                print(f"✅ Analytics saved locally for @{username}")

            return backend_json

        except Exception as e:
            print(f"❌ Error processing @{username}: {str(e)}")
            return None

    def process_multiple_accounts(self, usernames: List[str], delay_between_accounts: int = 60):
        """Process multiple Twitter accounts with delays"""
        print(f"🐦 Professional Twitter Data Collector")
        print("=" * 60)
        print(f"📊 Processing {len(usernames)} accounts")
        print(f"🏁 Backend Endpoint: {self.backend_endpoint}")
        print(f"⏰ Delay between accounts: {delay_between_accounts} seconds")

        all_results = {}

        for i, username in enumerate(usernames, 1):
            print(f"\n📍 Account {i}/{len(usernames)}: @{username}")
            print("-" * 40)

            result = self.process_account(username)
            all_results[username] = result

            # Add delay between accounts (except for the last one)
            if i < len(usernames):
                print(f"\n⏳ Waiting {delay_between_accounts} seconds before next account...")
                time.sleep(delay_between_accounts)

        # Summary
        print(f"\n📋 COLLECTION SUMMARY")
        print("=" * 60)
        successful = sum(1 for result in all_results.values() if result is not None)
        total = len(all_results)

        print(f"✅ Successfully collected: {successful}/{total} accounts")
        print(f"❌ Failed: {total - successful}/{total} accounts")

        for username, result in all_results.items():
            status = "✅ Success" if result else "❌ Failed"
            followers = result['twitter']['analytics']['followers'] if result else 0
            print(f"   @{username}: {status} ({followers:,} followers)")

        return all_results

def main():
    """Main function"""
    try:
        # Initialize collector
        collector = TwitterDataCollector()

        # Define accounts to process
        target_accounts = [
            'elonmusk',
            'nasa',
            'twitter'
        ]

        # Process all accounts
        results = collector.process_multiple_accounts(
            target_accounts,
            delay_between_accounts=30  # 30 seconds between accounts
        )

        print(f"\n🎉 Twitter data collection completed!")
        print(f"📁 All data saved in backend-compatible JSON format")
        print(f"🔄 Ready to sync with backend endpoint")

    except Exception as e:
        print(f"❌ Collection failed: {str(e)}")

if __name__ == "__main__":
    main()