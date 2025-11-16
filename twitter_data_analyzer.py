#!/usr/bin/env python3
"""
Twitter Data Analyzer - Fetches and analyzes Twitter data including likes, threads, and engagement metrics
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twitter_real_api import setup_twitter_real_api, get_twitter_real_analytics, test_twitter_connection, get_twitter_trending_topics
from social_media_analytics import generate_comprehensive_analytics_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TwitterDataAnalyzer:
    """Comprehensive Twitter data analyzer for fetching and analyzing social media data"""

    def __init__(self):
        self.twitter_api = None
        self.setup_api()

    def setup_api(self):
        """Setup Twitter API with credentials from environment variables"""
        try:
            client_id = os.getenv('TWITTER_CLIENT_ID')
            client_secret = os.getenv('TWITTER_CLIENT_SECRET')
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

            if not all([client_id, client_secret]):
                logger.error("❌ Missing Twitter credentials in environment variables")
                logger.info("Please set TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET in your .env file")
                return False

            self.twitter_api = setup_twitter_real_api(client_id, client_secret, bearer_token)

            # Test connection
            if test_twitter_connection():
                logger.info("✅ Twitter API connection established successfully")
                return True
            else:
                logger.warning("⚠️ Twitter API connection failed - will use fallback data")
                return True  # Continue with fallback data

        except Exception as e:
            logger.error(f"❌ Error setting up Twitter API: {str(e)}")
            return False

    def fetch_user_analytics(self, username: str) -> Dict[str, Any]:
        """Fetch comprehensive analytics for a Twitter user"""
        logger.info(f"📊 Fetching analytics for @{username}")

        try:
            analytics = get_twitter_real_analytics(username)

            # Add analysis timestamp
            analytics['analysis_timestamp'] = datetime.now().isoformat()
            analytics['data_source'] = 'real_api' if not analytics.get('is_fallback') else 'fallback'

            logger.info(f"✅ Successfully fetched analytics for @{username}")
            logger.info(f"   Followers: {analytics.get('followers', 0):,}")
            logger.info(f"   Engagement Rate: {analytics.get('engagement_rate', 0):.2f}%")
            logger.info(f"   Tweets Analyzed: {analytics.get('tweets_analyzed', 0)}")

            return analytics

        except Exception as e:
            logger.error(f"❌ Error fetching analytics for @{username}: {str(e)}")
            return {}

    def fetch_multiple_users_analytics(self, usernames: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch analytics for multiple Twitter users"""
        logger.info(f"📊 Fetching analytics for {len(usernames)} users")

        results = {}

        for username in usernames:
            try:
                analytics = self.fetch_user_analytics(username)
                if analytics:
                    results[username] = analytics

                # Add small delay to avoid rate limiting
                import time
                time.sleep(1)

            except Exception as e:
                logger.error(f"❌ Error processing @{username}: {str(e)}")
                continue

        logger.info(f"✅ Successfully fetched analytics for {len(results)} users")
        return results

    def analyze_tweet_threads(self, username: str, max_threads: int = 10) -> List[Dict[str, Any]]:
        """Analyze tweet threads from a user"""
        logger.info(f"🧵 Analyzing tweet threads from @{username}")

        # This is a placeholder for thread analysis functionality
        # In a full implementation, you would:
        # 1. Fetch user's tweets
        # 2. Identify threads (connected tweets)
        # 3. Analyze thread performance

        try:
            # For now, we'll create a mock thread analysis
            analytics = self.fetch_user_analytics(username)

            threads = []
            for i in range(min(max_threads, 5)):
                thread = {
                    'thread_id': f"thread_{i+1}",
                    'username': username,
                    'tweet_count': i + 1,
                    'total_likes': analytics.get('tweet_likes', 0) // (max_threads),
                    'total_retweets': analytics.get('tweet_retweets', 0) // (max_threads),
                    'total_replies': analytics.get('tweet_replies', 0) // (max_threads),
                    'engagement_rate': analytics.get('engagement_rate', 0),
                    'created_at': (datetime.now() - timedelta(hours=i*12)).isoformat()
                }
                threads.append(thread)

            logger.info(f"✅ Analyzed {len(threads)} threads from @{username}")
            return threads

        except Exception as e:
            logger.error(f"❌ Error analyzing threads for @{username}: {str(e)}")
            return []

    def get_trending_analysis(self) -> Dict[str, Any]:
        """Fetch and analyze trending topics"""
        logger.info("🔥 Fetching trending topics")

        try:
            trending_data = get_twitter_trending_topics()

            # Add analysis metadata
            trending_data['analysis_timestamp'] = datetime.now().isoformat()
            trending_data['topics_count'] = len(trending_data.get('topics', []))

            logger.info(f"✅ Found {trending_data['topics_count']} trending topics")
            return trending_data

        except Exception as e:
            logger.error(f"❌ Error fetching trending topics: {str(e)}")
            return {'topics': [], 'analysis_timestamp': datetime.now().isoformat()}

    def generate_comprehensive_report(self, usernames: List[str], include_trending: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""
        logger.info("📋 Generating comprehensive Twitter analysis report")

        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'usernames_analyzed': usernames,
                'include_trending': include_trending,
                'analyzer_version': '1.0.0'
            },
            'user_analytics': {},
            'thread_analysis': {},
            'trending_topics': {},
            'summary_insights': {}
        }

        try:
            # Fetch user analytics
            report['user_analytics'] = self.fetch_multiple_users_analytics(usernames)

            # Analyze threads for each user
            for username in usernames:
                report['thread_analysis'][username] = self.analyze_tweet_threads(username)

            # Fetch trending topics if requested
            if include_trending:
                report['trending_topics'] = self.get_trending_analysis()

            # Generate summary insights
            report['summary_insights'] = self._generate_summary_insights(report)

            # Save report to file
            report_filename = f"twitter_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"✅ Comprehensive report saved to {report_filename}")
            return report

        except Exception as e:
            logger.error(f"❌ Error generating comprehensive report: {str(e)}")
            return report

    def _generate_summary_insights(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary insights from the collected data"""
        insights = {
            'total_users_analyzed': len(report['user_analytics']),
            'total_followers': 0,
            'total_tweets': 0,
            'average_engagement_rate': 0,
            'top_performers': {},
            'trending_summary': {}
        }

        try:
            # Calculate aggregate metrics
            total_engagement_rate = 0
            user_count = 0

            for username, analytics in report['user_analytics'].items():
                if analytics:
                    insights['total_followers'] += analytics.get('followers', 0)
                    insights['total_tweets'] += analytics.get('tweets', 0)
                    total_engagement_rate += analytics.get('engagement_rate', 0)
                    user_count += 1

            if user_count > 0:
                insights['average_engagement_rate'] = round(total_engagement_rate / user_count, 2)

            # Find top performers
            if report['user_analytics']:
                sorted_users = sorted(
                    report['user_analytics'].items(),
                    key=lambda x: x[1].get('followers', 0),
                    reverse=True
                )
                insights['top_performers']['most_followers'] = sorted_users[0][0] if sorted_users else None

                sorted_users = sorted(
                    report['user_analytics'].items(),
                    key=lambda x: x[1].get('engagement_rate', 0),
                    reverse=True
                )
                insights['top_performers']['highest_engagement'] = sorted_users[0][0] if sorted_users else None

            # Trending summary
            trending_topics = report.get('trending_topics', {}).get('topics', [])
            insights['trending_summary'] = {
                'total_topics': len(trending_topics),
                'top_topics': [topic.get('name', '') for topic in trending_topics[:5]] if trending_topics else []
            }

        except Exception as e:
            logger.error(f"❌ Error generating summary insights: {str(e)}")

        return insights

def main():
    """Main function to demonstrate Twitter data analysis"""
    print("🐦 Twitter Data Analyzer")
    print("=" * 50)

    # Initialize analyzer
    analyzer = TwitterDataAnalyzer()

    # Example usernames to analyze
    example_usernames = [
        'elonmusk',
        'nasa',
        'twitter',
        'github'
    ]

    print(f"\n📊 Analyzing Twitter data for: {', '.join(example_usernames)}")

    # Generate comprehensive report
    report = analyzer.generate_comprehensive_report(
        usernames=example_usernames,
        include_trending=True
    )

    # Display summary
    print("\n" + "=" * 50)
    print("📋 ANALYSIS SUMMARY")
    print("=" * 50)

    insights = report.get('summary_insights', {})
    print(f"Total Users Analyzed: {insights.get('total_users_analyzed', 0)}")
    print(f"Total Followers: {insights.get('total_followers', 0):,}")
    print(f"Total Tweets: {insights.get('total_tweets', 0):,}")
    print(f"Average Engagement Rate: {insights.get('average_engagement_rate', 0):.2f}%")

    if insights.get('top_performers', {}).get('most_followers'):
        print(f"Most Followed: @{insights['top_performers']['most_followers']}")

    if insights.get('top_performers', {}).get('highest_engagement'):
        print(f"Highest Engagement: @{insights['top_performers']['highest_engagement']}")

    trending_summary = insights.get('trending_summary', {})
    if trending_summary.get('top_topics'):
        print(f"Top Trending Topics: {', '.join(trending_summary['top_topics'][:3])}")

    print(f"\n📁 Full report saved to: twitter_analysis_report_*.json")
    print("📝 Check the detailed JSON file for complete analytics data")

if __name__ == "__main__":
    main()