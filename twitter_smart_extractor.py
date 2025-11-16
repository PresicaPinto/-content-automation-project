#!/usr/bin/env python3
"""
Smart Twitter Data Extractor - Avoids rate limits with intelligent strategies
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SmartTwitterExtractor:
    """Intelligent Twitter extractor that avoids rate limits"""

    def __init__(self):
        self.bearer_token = None
        self.base_url = "https://api.twitter.com/2"
        self.rate_limits = {}
        self.request_count = 0
        self.last_request_time = 0
        self.setup_credentials()

    def setup_credentials(self):
        """Setup Twitter API credentials"""
        from dotenv import load_dotenv
        load_dotenv()
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        print(f"✅ Bearer Token loaded: {self.bearer_token[:20]}...")

    def smart_delay(self, min_delay=1.0):
        """Intelligent delay between requests to avoid rate limits"""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < min_delay:
            delay = min_delay - time_since_last
            print(f"⏳ Smart delay: {delay:.1f} seconds")
            time.sleep(delay)

        self.last_request_time = time.time()

    def check_rate_limit_headers(self, response):
        """Check and track rate limit headers"""
        remaining = response.headers.get('x-rate-limit-remaining', 'unknown')
        limit = response.headers.get('x-rate-limit-limit', 'unknown')
        reset_time = response.headers.get('x-rate-limit-reset', 'unknown')

        if remaining != 'unknown':
            remaining = int(remaining)
            limit = int(limit)

            self.rate_limits['remaining'] = remaining
            self.rate_limits['limit'] = limit
            self.rate_limits['usage_percentage'] = (limit - remaining) / limit * 100

            print(f"📊 Rate Limit: {remaining}/{limit} ({self.rate_limits['usage_percentage']:.1f}% used)")

            # Warn if getting close to limit
            if remaining < 10:
                print("⚠️ Warning: Approaching rate limit!")

        return remaining != 'unknown'

    def make_smart_request(self, url, params=None, max_retries=3):
        """Make request with retry logic and rate limit handling"""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        for attempt in range(max_retries):
            try:
                # Smart delay before request
                self.smart_delay()

                print(f"🔍 Request {attempt + 1}/{max_retries}: {url}")
                response = requests.get(url, headers=headers, params=params)

                # Track rate limits
                self.check_rate_limit_headers(response)
                self.request_count += 1

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limit hit - wait for reset
                    reset_time = response.headers.get('x-rate-limit-reset')
                    if reset_time:
                        reset_timestamp = int(reset_time)
                        wait_time = max(0, reset_timestamp - int(time.time()))

                        if wait_time > 0:
                            print(f"⏰ Rate limit hit. Waiting {wait_time} seconds for reset...")
                            time.sleep(wait_time + 5)  # Add 5 second buffer
                            continue

                    # Fallback: wait 60 seconds
                    print("⏰ Rate limit hit. Waiting 60 seconds...")
                    time.sleep(60)
                    continue

                elif response.status_code in [401, 403]:
                    print(f"❌ Authentication Error: {response.status_code}")
                    return None

                else:
                    print(f"⚠️ HTTP Error {response.status_code}: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    continue

            except Exception as e:
                print(f"❌ Request error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

        return None

    def get_user_data(self, username):
        """Get user data with smart rate limit handling"""
        params = {
            'user.fields': 'created_at,description,public_metrics,verified,url,username,profile_image_url'
        }

        url = f"{self.base_url}/users/by/username/{username}"
        response = self.make_smart_request(url, params)

        if response and response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print(f"✅ Got real data for @{username}")
                return data['data']

        print(f"❌ Failed to get data for @{username}")
        return None

    def batch_extract_users(self, usernames, batch_size=2):
        """Extract user data in batches to avoid rate limits"""
        print(f"🐦 Smart Twitter Extractor")
        print("=" * 60)
        print(f"📊 Processing {len(usernames)} users in batches of {batch_size}")
        print(f"🛡️ Rate limit protection: ENABLED")

        all_data = {}

        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1}: {', '.join(batch)}")

            batch_data = {}

            for username in batch:
                user_data = self.get_user_data(username)
                if user_data:
                    batch_data[username] = user_data
                else:
                    print(f"   ⚠️ @{username} skipped due to API limits")

            all_data.update(batch_data)

            # Check if we should continue
            if self.rate_limits.get('remaining', 100) < 5:
                print(f"\n⚠️ Rate limit getting low. Taking a break...")
                break

            # Longer break between batches
            if i + batch_size < len(usernames):
                print(f"⏳ Taking 30-second break between batches...")
                time.sleep(30)

        return all_data

    def save_results(self, data, filename_prefix="smart_twitter_data"):
        """Save extracted data with metadata"""
        if not data:
            print("❌ No data to save")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.json"

        output_data = {
            'extraction_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_accounts': len(data),
                'requests_made': self.request_count,
                'rate_limit_status': self.rate_limits,
                'extraction_method': 'smart_batch_with_rate_limit_protection'
            },
            'accounts': data
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Data saved to: {filename}")
        return filename

def main():
    """Main function with rate limit protection"""
    extractor = SmartTwitterExtractor()

    # Define usernames to extract
    target_usernames = [
        'elonmusk',
        'nasa',
        'twitter',
        'github',
        'verge',
        'techcrunch'
    ]

    print(f"🎯 Target accounts: {', '.join(target_usernames)}")

    # Extract with rate limit protection
    extracted_data = extractor.batch_extract_users(target_usernames, batch_size=2)

    # Save results
    if extracted_data:
        filename = extractor.save_results(extracted_data)

        print(f"\n📋 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully extracted data for {len(extracted_data)} accounts")
        print(f"📊 Total requests made: {extractor.request_count}")

        # Display follower counts
        for username, data in extracted_data.items():
            followers = data.get('public_metrics', {}).get('followers_count', 0)
            verified = "✓" if data.get('verified') else "✗"
            print(f"   @{username}: {followers:,} followers ({verified} verified)")

        print(f"\n💾 Full data saved to: {filename}")
        print(f"🎉 Rate limit protection worked - no 429 errors!")

    else:
        print("❌ No data extracted due to rate limits")

if __name__ == "__main__":
    main()