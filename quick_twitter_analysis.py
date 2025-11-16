#!/usr/bin/env python3
"""
Quick Twitter Analysis Demo - Extract and analyze Twitter data for insights
Run this script to fetch and analyze Twitter data immediately
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_twitter_analyzer():
    """Load and initialize Twitter analyzer"""
    try:
        from twitter_real_api import setup_twitter_real_api
        from twitter_data_analyzer import TwitterDataAnalyzer

        # Initialize analyzer
        analyzer = TwitterDataAnalyzer()
        return analyzer

    except Exception as e:
        print(f"❌ Error loading Twitter analyzer: {str(e)}")
        return None

def extract_and_analyze_data():
    """Main function to extract and analyze Twitter data"""
    print("🐦 Quick Twitter Data Analysis")
    print("=" * 60)

    # Load analyzer
    analyzer = load_twitter_analyzer()
    if not analyzer:
        print("❌ Failed to initialize Twitter analyzer")
        return

    # Define usernames to analyze (you can modify this list)
    target_usernames = [
        'elonmusk',
        'nasa',
        'github',
        'techcrunch'
    ]

    print(f"\n📊 Extracting data for: {', '.join(target_usernames)}")
    print("This may take a moment...")

    # Extract data for each user
    extracted_data = {}

    for username in target_usernames:
        print(f"\n🔍 Extracting data for @{username}...")

        try:
            # Get user analytics
            analytics = analyzer.fetch_user_analytics(username)
            if analytics:
                extracted_data[username] = analytics

                # Display key metrics
                print(f"   ✅ Followers: {analytics.get('followers', 0):,}")
                print(f"   ❤️  Total Likes: {analytics.get('tweet_likes', 0):,}")
                print(f"   🔄 Retweets: {analytics.get('tweet_retweets', 0):,}")
                print(f"   💬 Replies: {analytics.get('tweet_replies', 0):,}")
                print(f"   📈 Engagement Rate: {analytics.get('engagement_rate', 0):.2f}%")
                print(f"   📱 Tweets Analyzed: {analytics.get('tweets_analyzed', 0)}")
            else:
                print(f"   ❌ Failed to fetch data for @{username}")

        except Exception as e:
            print(f"   ❌ Error analyzing @{username}: {str(e)}")

    # Perform analysis
    print(f"\n📈 ANALYSIS RESULTS")
    print("=" * 60)

    if extracted_data:
        # Calculate total metrics
        total_followers = sum(data.get('followers', 0) for data in extracted_data.values())
        total_likes = sum(data.get('tweet_likes', 0) for data in extracted_data.values())
        total_retweets = sum(data.get('tweet_retweets', 0) for data in extracted_data.values())
        avg_engagement = sum(data.get('engagement_rate', 0) for data in extracted_data.values()) / len(extracted_data)

        print(f"📊 Aggregate Metrics:")
        print(f"   Total Followers Across Accounts: {total_followers:,}")
        print(f"   Total Likes: {total_likes:,}")
        print(f"   Total Retweets: {total_retweets:,}")
        print(f"   Average Engagement Rate: {avg_engagement:.2f}%")

        # Find top performers
        most_followed = max(extracted_data.items(), key=lambda x: x[1].get('followers', 0))
        highest_engagement = max(extracted_data.items(), key=lambda x: x[1].get('engagement_rate', 0))

        print(f"\n🏆 Top Performers:")
        print(f"   Most Followed: @{most_followed[0]} ({most_followed[1].get('followers', 0):,} followers)")
        print(f"   Highest Engagement: @{highest_engagement[0]} ({highest_engagement[1].get('engagement_rate', 0):.2f}%)")

        # Save detailed data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"twitter_extracted_data_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'extraction_timestamp': datetime.now().isoformat(),
                'data_source': 'twitter_api',
                'accounts_analyzed': list(extracted_data.keys()),
                'extracted_data': extracted_data
            }, f, indent=2)

        print(f"\n💾 Detailed data saved to: {filename}")

        # Generate analysis insights
        print(f"\n💡 Key Insights:")
        print(f"   • Analyzed {len(extracted_data)} Twitter accounts")
        print(f"   • Total social reach: {total_followers:,} followers")
        print(f"   • Content engagement: {total_likes:,} total likes")

        # Engagement analysis
        high_engagement_accounts = [user for user, data in extracted_data.items()
                                   if data.get('engagement_rate', 0) > 3.0]

        if high_engagement_accounts:
            print(f"   • High engagement accounts (>3%): {', '.join(high_engagement_accounts)}")

        # Activity analysis
        most_active = max(extracted_data.items(), key=lambda x: x[1].get('tweets', 0))
        print(f"   • Most active: @{most_active[0]} ({most_active[1].get('tweets', 0)} tweets)")

    else:
        print("❌ No data was successfully extracted")
        print("Please check your Twitter API credentials in the .env file")

def check_credentials():
    """Check if Twitter credentials are properly configured"""
    print("🔧 Checking Twitter API credentials...")

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass

    client_id = os.getenv('TWITTER_CLIENT_ID')
    client_secret = os.getenv('TWITTER_CLIENT_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not all([client_id, client_secret]):
        print("❌ Missing required credentials:")
        print("   • TWITTER_CLIENT_ID")
        print("   • TWITTER_CLIENT_SECRET")
        print("\n📝 Please update your .env file with your Twitter API credentials")
        print("   Get credentials from: https://developer.twitter.com/")
        return False

    if not bearer_token:
        print("⚠️  No TWITTER_BEARER_TOKEN found")
        print("   The system will try to generate one automatically")
        print("   You can also add it to your .env file for better performance")

    print("✅ Twitter API credentials found")
    return True

if __name__ == "__main__":
    # Check credentials first
    if check_credentials():
        # Extract and analyze data
        extract_and_analyze_data()
    else:
        print("\n🚨 Cannot proceed without Twitter API credentials")
        print("Please follow the setup instructions above and try again")