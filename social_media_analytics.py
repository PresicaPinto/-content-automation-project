#!/usr/bin/env python3
"""
Social Media Analytics Module
Integrates with LinkedIn, Twitter/X.com, and Instagram APIs for analytics
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LinkedInAnalytics:
    followers: int
    engagement_rate: float
    profile_views: int
    post_impressions: int
    search_appearances: int
    post_clicks: int
    post_likes: int
    post_comments: int
    post_shares: int
    date_collected: datetime

@dataclass
class TwitterAnalytics:
    followers: int
    following: int
    tweets: int
    tweet_impressions: int
    profile_views: int
    tweet_likes: int
    tweet_retweets: int
    tweet_replies: int
    tweet_quotes: int
    engagement_rate: float
    date_collected: datetime

@dataclass
class InstagramAnalytics:
    followers: int
    following: int
    posts: int
    reach: int
    impressions: int
    profile_views: int
    website_clicks: int
    likes: int
    comments: int
    saves: int
    engagement_rate: float
    date_collected: datetime

class LinkedInAnalyticsManager:
    def __init__(self, client_id: str, client_secret: str, access_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.base_url_ugc = "https://api.linkedin.com/v2/ugcPosts"
        self.headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    def get_access_token(self, redirect_uri: str, code: str) -> str:
        """Exchange authorization code for access token"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=data
        )

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
            return self.access_token
        else:
            logger.error(f"Failed to get access token: {response.text}")
            return None

    def get_profile_analytics(self, person_urn: str) -> Optional[LinkedInAnalytics]:
        """Get LinkedIn profile analytics"""
        if not self.access_token:
            logger.error("No access token available")
            return None

        try:
            # Get profile engagement data
            engagement_url = f"{self.base_url}/socialActions/{person_urn}"
            response = requests.get(engagement_url, headers=self.headers)

            if response.status_code != 200:
                logger.error(f"Failed to get LinkedIn engagement: {response.text}")
                return self._get_empty_linkedin_analytics()

            engagement_data = response.json()

            # Get profile statistics
            profile_stats = self._get_profile_statistics(person_urn)

            return LinkedInAnalytics(
                followers=profile_stats.get("followers", 0),
                engagement_rate=engagement_data.get("engagementRate", 0.0),
                profile_views=profile_stats.get("profileViews", 0),
                post_impressions=engagement_data.get("impressions", 0),
                search_appearances=profile_stats.get("searchAppearances", 0),
                post_clicks=engagement_data.get("clicks", 0),
                post_likes=engagement_data.get("likes", 0),
                post_comments=engagement_data.get("comments", 0),
                post_shares=engagement_data.get("shares", 0),
                date_collected=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error getting LinkedIn analytics: {str(e)}")
            return self._get_empty_linkedin_analytics()

    def _get_profile_statistics(self, person_urn: str) -> Dict:
        """Get LinkedIn profile statistics"""
        # This would require additional API calls to LinkedIn
        # Return empty state when no real data available
        return {
            "followers": 0,
            "profileViews": 0,
            "searchAppearances": 0,
            "connected": False
        }

    def _get_empty_linkedin_analytics(self) -> LinkedInAnalytics:
        """Return empty LinkedIn analytics when no real data available"""
        return LinkedInAnalytics(
            followers=0,
            engagement_rate=0,
            profile_views=0,
            post_impressions=0,
            search_appearances=0,
            post_clicks=0,
            post_likes=0,
            post_comments=0,
            post_shares=0,
            date_collected=datetime.now()
        )

class TwitterAnalyticsManager:
    def __init__(self, client_id: str, client_secret: str, bearer_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {"Authorization": f"Bearer {bearer_token}"} if bearer_token else {}

    def get_bearer_token(self) -> str:
        """Get bearer token using client credentials"""
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = requests.utils.quote(credentials)

            headers = {
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Authorization": f"Basic {encoded_credentials}"
            }

            data = "grant_type=client_credentials"
            response = requests.post(
                "https://api.twitter.com/oauth2/token",
                headers=headers,
                data=data,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.bearer_token = token_data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
                logger.info("Successfully obtained Twitter bearer token")
                return self.bearer_token
            else:
                logger.error(f"Failed to get bearer token: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting Twitter bearer token: {str(e)}")
            return None

    def get_user_analytics(self, username: str) -> Optional[TwitterAnalytics]:
        """Get comprehensive Twitter analytics for a user"""
        try:
            # First get user information
            user_data = self._get_user_by_username(username)
            if not user_data:
                return None

            user_id = user_data.get('id')

            # Get user metrics
            metrics = self._get_user_metrics(user_id)

            # Get tweet analytics (last 100 tweets)
            tweet_analytics = self._get_recent_tweets_analytics(user_id)

            # Calculate engagement rate
            total_likes = tweet_analytics.get('total_likes', 0)
            total_retweets = tweet_analytics.get('total_retweets', 0)
            total_replies = tweet_analytics.get('total_replies', 0)
            total_tweets = tweet_analytics.get('total_tweets', 0)
            total_impressions = tweet_analytics.get('total_impressions', 0)

            # Engagement rate calculation
            total_engagement = total_likes + total_retweets + total_replies
            avg_impressions_per_tweet = total_impressions / max(1, total_tweets)
            engagement_rate = (total_engagement / max(1, avg_impressions_per_tweet)) * 100 if avg_impressions_per_tweet > 0 else 0

            return TwitterAnalytics(
                followers=user_data.get('public_metrics', {}).get('followers_count', 0),
                following=user_data.get('public_metrics', {}).get('following_count', 0),
                tweets=user_data.get('public_metrics', {}).get('tweet_count', 0),
                tweet_impressions=total_impressions,
                profile_views=metrics.get('profile_views', 0),
                tweet_likes=total_likes,
                tweet_retweets=total_retweets,
                tweet_replies=total_replies,
                tweet_quotes=tweet_analytics.get('total_quotes', 0),
                engagement_rate=round(engagement_rate, 2),
                date_collected=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error getting Twitter analytics: {str(e)}")
            return None

    def _get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user information by username"""
        try:
            # Remove @ if present
            clean_username = username.lstrip('@')

            url = f"{self.base_url}/users/by/username/{clean_username}"
            params = {
                "user.fields": "public_metrics,description,created_at,verified,location,url"
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return data.get('data')
            else:
                logger.error(f"Failed to get user {username}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            return None

    def _get_user_metrics(self, user_id: str) -> Dict:
        """Get detailed user metrics"""
        try:
            # Return empty state when no real data available
            # In a real implementation, you'd use Twitter's premium APIs
            return {
                "profile_views": 0,
                "connected": False
            }

        except Exception as e:
            logger.error(f"Error getting user metrics: {str(e)}")
            return {"profile_views": 0, "connected": False}

    def _get_recent_tweets_analytics(self, user_id: str, count: int = 100) -> Dict:
        """Get analytics for recent tweets"""
        try:
            url = f"{self.base_url}/users/{user_id}/tweets"
            params = {
                "tweet.fields": "public_metrics,created_at",
                "max_results": min(count, 100),  # Twitter API limit
                "exclude": "retweets,replies"
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])

                total_likes = 0
                total_retweets = 0
                total_replies = 0
                total_quotes = 0
                total_impressions = 0

                for tweet in tweets:
                    metrics = tweet.get('public_metrics', {})
                    total_likes += metrics.get('like_count', 0)
                    total_retweets += metrics.get('retweet_count', 0)
                    total_replies += metrics.get('reply_count', 0)
                    total_quotes += metrics.get('quote_count', 0)
                    total_impressions += metrics.get('impression_count', 0)

                return {
                    "total_tweets": len(tweets),
                    "total_likes": total_likes,
                    "total_retweets": total_retweets,
                    "total_replies": total_replies,
                    "total_quotes": total_quotes,
                    "total_impressions": total_impressions
                }
            else:
                logger.error(f"Failed to get tweets: {response.text}")
                return self._get_empty_tweet_analytics()

        except Exception as e:
            logger.error(f"Error getting recent tweets analytics: {str(e)}")
            return self._get_empty_tweet_analytics()

    def _get_empty_tweet_analytics(self) -> Dict:
        """Return empty tweet analytics when no real data available"""
        return {
            "total_tweets": 0,
            "total_likes": 0,
            "total_retweets": 0,
            "total_replies": 0,
            "total_quotes": 0,
            "total_impressions": 0,
            "connected": False
        }

    def get_trending_topics(self, woeid: int = 1) -> List[Dict]:
        """Get trending topics (using Twitter API v1.1 for this)"""
        try:
            # Note: This would require OAuth 1.0a authentication
            # Return empty list when no real data available
            return []

        except Exception as e:
            logger.error(f"Error getting trending topics: {str(e)}")
            return []

    def get_analytics_summary(self, username: str) -> Dict:
        """Get a comprehensive analytics summary"""
        analytics = self.get_user_analytics(username)
        if not analytics:
            return {}

        return {
            "followers": analytics.followers,
            "following": analytics.following,
            "tweets": analytics.tweets,
            "engagement_rate": analytics.engagement_rate,
            "avg_likes_per_tweet": analytics.tweet_likes / max(1, analytics.tweets),
            "avg_retweets_per_tweet": analytics.tweet_retweets / max(1, analytics.tweets),
            "total_impressions": analytics.tweet_impressions,
            "profile_views": analytics.profile_views,
            "influence_score": self._calculate_influence_score(analytics),
            "growth_potential": self._calculate_growth_potential(analytics)
        }

    def _calculate_influence_score(self, analytics: TwitterAnalytics) -> float:
        """Calculate influence score based on metrics"""
        try:
            # Normalize metrics (0-100 scale)
            followers_score = min(100, analytics.followers / 1000)  # 1k followers = 1 point
            engagement_score = min(100, analytics.engagement_rate * 10)  # 10% engagement = 100 points
            activity_score = min(100, analytics.tweets / 10)  # 10 tweets = 1 point

            # Weighted average
            influence_score = (followers_score * 0.4 + engagement_score * 0.4 + activity_score * 0.2)
            return round(influence_score, 1)

        except Exception:
            return 0.0

    def _calculate_growth_potential(self, analytics: TwitterAnalytics) -> str:
        """Calculate growth potential based on current metrics"""
        try:
            if analytics.engagement_rate > 5.0:
                return "High"
            elif analytics.engagement_rate > 2.0:
                return "Medium"
            else:
                return "Low"

        except Exception:
            return "Unknown"

    def get_user_analytics(self, username: str) -> Optional[TwitterAnalytics]:
        """Get Twitter user analytics"""
        if not self.bearer_token:
            logger.error("No bearer token available")
            return None

        try:
            # Get user information
            user_url = f"{self.base_url}/users/by/username/{username}"
            params = {
                "user.fields": "public_metrics,description,created_at,verified"
            }

            response = requests.get(user_url, headers=self.headers, params=params)

            if response.status_code != 200:
                logger.error(f"Failed to get Twitter user data: {response.text}")
                return self._get_empty_twitter_analytics()

            user_data = response.json()
            user_info = user_data.get("data", {})
            metrics = user_info.get("public_metrics", {})

            # Get recent tweets analytics
            tweets_analytics = self._get_recent_tweets_analytics(username)

            # Calculate engagement rate
            total_engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0)
            total_tweets = metrics.get("tweet_count", 1)
            avg_engagement = total_engagement / total_tweets if total_tweets > 0 else 0
            engagement_rate = (avg_engagement / metrics.get("followers_count", 1)) * 100

            return TwitterAnalytics(
                followers=metrics.get("followers_count", 0),
                following=metrics.get("following_count", 0),
                tweets=metrics.get("tweet_count", 0),
                tweet_impressions=tweets_analytics.get("impressions", 0),
                profile_views=tweets_analytics.get("profile_views", 0),
                tweet_likes=metrics.get("like_count", 0),
                tweet_retweets=metrics.get("retweet_count", 0),
                tweet_replies=tweets_analytics.get("replies", 0),
                tweet_quotes=tweets_analytics.get("quotes", 0),
                engagement_rate=round(engagement_rate, 2),
                date_collected=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error getting Twitter analytics: {str(e)}")
            return self._get_empty_twitter_analytics()

    def _get_recent_tweets_analytics(self, username: str) -> Dict:
        """Get analytics for recent tweets"""
        try:
            # Get recent tweets
            tweets_url = f"{self.base_url}/tweets/search/recent"
            params = {
                "query": f"from:{username}",
                "tweet.fields": "public_metrics,created_at",
                "max_results": 10
            }

            response = requests.get(tweets_url, headers=self.headers, params=params)

            if response.status_code == 200:
                tweets_data = response.json()
                tweets = tweets_data.get("data", [])

                total_impressions = 0
                total_replies = 0
                total_quotes = 0

                for tweet in tweets:
                    metrics = tweet.get("public_metrics", {})
                    total_impressions += metrics.get("impression_count", 0)
                    total_replies += metrics.get("reply_count", 0)
                    total_quotes += metrics.get("quote_count", 0)

                return {
                    "impressions": total_impressions,
                    "replies": total_replies,
                    "quotes": total_quotes,
                    "profile_views": len(tweets) * 15  # Estimate
                }
            else:
                return {"impressions": 0, "replies": 0, "quotes": 0, "profile_views": 0}

        except Exception as e:
            logger.error(f"Error getting recent tweets analytics: {str(e)}")
            return {"impressions": 0, "replies": 0, "quotes": 0, "profile_views": 0}

    def _get_empty_twitter_analytics(self) -> TwitterAnalytics:
        """Return empty Twitter analytics when no real data available"""
        return TwitterAnalytics(
            followers=0,
            following=0,
            tweets=0,
            tweet_impressions=0,
            profile_views=0,
            tweet_likes=0,
            tweet_retweets=0,
            tweet_replies=0,
            tweet_quotes=0,
            engagement_rate=0,
            date_collected=datetime.now()
        )

class InstagramAnalyticsManager:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def get_business_analytics(self, instagram_business_id: str) -> Optional[InstagramAnalytics]:
        """Get Instagram business account analytics"""
        if not self.access_token:
            logger.error("No access token available")
            return None

        try:
            # Get account insights
            insights_url = f"{self.base_url}/{instagram_business_id}/insights"
            params = {
                "metric": "impressions,reach,profile_views,website_clicks",
                "period": "day",
                "access_token": self.access_token
            }

            response = requests.get(insights_url, params=params)

            if response.status_code != 200:
                logger.error(f"Failed to get Instagram insights: {response.text}")
                return self._get_empty_instagram_analytics()

            insights_data = response.json()

            # Get account media for engagement calculation
            media_analytics = self._get_media_analytics(instagram_business_id)

            return InstagramAnalytics(
                followers=media_analytics.get("followers", 0),
                following=media_analytics.get("following", 0),
                posts=media_analytics.get("posts", 0),
                reach=self._extract_metric(insights_data, "reach"),
                impressions=self._extract_metric(insights_data, "impressions"),
                profile_views=self._extract_metric(insights_data, "profile_views"),
                website_clicks=self._extract_metric(insights_data, "website_clicks"),
                likes=media_analytics.get("likes", 0),
                comments=media_analytics.get("comments", 0),
                saves=media_analytics.get("saves", 0),
                engagement_rate=media_analytics.get("engagement_rate", 0.0),
                date_collected=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error getting Instagram analytics: {str(e)}")
            return self._get_empty_instagram_analytics()

    def _get_media_analytics(self, instagram_business_id: str) -> Dict:
        """Get media analytics for engagement calculation"""
        try:
            media_url = f"{self.base_url}/{instagram_business_id}/media"
            params = {
                "fields": "like_count,comments_count,media_type",
                "limit": 25,
                "access_token": self.access_token
            }

            response = requests.get(media_url, params=params)

            if response.status_code == 200:
                media_data = response.json()
                media_items = media_data.get("data", [])

                total_likes = 0
                total_comments = 0
                total_saves = 0

                for media in media_items:
                    total_likes += media.get("like_count", 0)
                    total_comments += media.get("comments_count", 0)
                    total_saves += media.get("saved_count", 0)

                # Get followers count
                account_url = f"{self.base_url}/{instagram_business_id}"
                account_params = {"fields": "followers_count,follows_count,media_count", "access_token": self.access_token}
                account_response = requests.get(account_url, params=account_params)

                followers = 0
                following = 0
                posts = len(media_items)

                if account_response.status_code == 200:
                    account_data = account_response.json()
                    followers = account_data.get("followers_count", 0)
                    following = account_data.get("follows_count", 0)
                    posts = account_data.get("media_count", len(media_items))

                # Calculate engagement rate
                total_engagement = total_likes + total_comments + total_saves
                engagement_rate = (total_engagement / followers * 100) if followers > 0 else 0

                return {
                    "followers": followers,
                    "following": following,
                    "posts": posts,
                    "likes": total_likes,
                    "comments": total_comments,
                    "saves": total_saves,
                    "engagement_rate": round(engagement_rate, 2)
                }
            else:
                return {"followers": 0, "engagement_rate": 0.0}

        except Exception as e:
            logger.error(f"Error getting media analytics: {str(e)}")
            return {"followers": 0, "engagement_rate": 0.0}

    def _extract_metric(self, insights_data: Dict, metric_name: str) -> int:
        """Extract metric value from insights data"""
        try:
            data = insights_data.get("data", [])
            for metric in data:
                if metric.get("name") == metric_name:
                    values = metric.get("values", [])
                    if values:
                        return values[0].get("value", 0)
            return 0
        except Exception:
            return 0

    def _get_empty_instagram_analytics(self) -> InstagramAnalytics:
        """Return empty Instagram analytics when no real data available"""
        return InstagramAnalytics(
            followers=0,
            following=0,
            posts=0,
            reach=0,
            impressions=0,
            profile_views=0,
            website_clicks=0,
            likes=0,
            comments=0,
            saves=0,
            engagement_rate=0,
            date_collected=datetime.now()
        )

class SocialMediaAnalyticsManager:
    def __init__(self):
        self.linkedin_manager = None
        self.twitter_manager = None
        self.instagram_manager = None

    def setup_linkedin(self, client_id: str, client_secret: str, access_token: str = None):
        """Setup LinkedIn analytics manager"""
        self.linkedin_manager = LinkedInAnalyticsManager(client_id, client_secret, access_token)

    def setup_twitter(self, client_id: str, client_secret: str, bearer_token: str = None):
        """Setup Twitter analytics manager"""
        self.twitter_manager = TwitterAnalyticsManager(client_id, client_secret, bearer_token)

    def setup_instagram(self, access_token: str):
        """Setup Instagram analytics manager"""
        self.instagram_manager = InstagramAnalyticsManager(access_token)

    def get_all_analytics(self, linkedin_urn: str = None, twitter_username: str = None,
                         instagram_business_id: str = None) -> Dict:
        """Get analytics from all configured platforms"""
        results = {}

        if self.linkedin_manager and linkedin_urn:
            try:
                linkedin_data = self.linkedin_manager.get_profile_analytics(linkedin_urn)
                if linkedin_data:
                    results["linkedin"] = {
                        "followers": linkedin_data.followers,
                        "engagement_rate": linkedin_data.engagement_rate,
                        "profile_views": linkedin_data.profile_views,
                        "post_impressions": linkedin_data.post_impressions,
                        "post_likes": linkedin_data.post_likes,
                        "post_comments": linkedin_data.post_comments,
                        "post_shares": linkedin_data.post_shares,
                        "date_collected": linkedin_data.date_collected.isoformat()
                    }
            except Exception as e:
                logger.error(f"LinkedIn analytics error: {str(e)}")

        if self.twitter_manager and twitter_username:
            try:
                twitter_data = self.twitter_manager.get_user_analytics(twitter_username)
                if twitter_data:
                    results["twitter"] = {
                        "followers": twitter_data.followers,
                        "following": twitter_data.following,
                        "tweets": twitter_data.tweets,
                        "tweet_impressions": twitter_data.tweet_impressions,
                        "profile_views": twitter_data.profile_views,
                        "tweet_likes": twitter_data.tweet_likes,
                        "tweet_retweets": twitter_data.tweet_retweets,
                        "tweet_replies": twitter_data.tweet_replies,
                        "engagement_rate": twitter_data.engagement_rate,
                        "date_collected": twitter_data.date_collected.isoformat()
                    }
            except Exception as e:
                logger.error(f"Twitter analytics error: {str(e)}")

        if self.instagram_manager and instagram_business_id:
            try:
                instagram_data = self.instagram_manager.get_business_analytics(instagram_business_id)
                if instagram_data:
                    results["instagram"] = {
                        "followers": instagram_data.followers,
                        "following": instagram_data.following,
                        "posts": instagram_data.posts,
                        "reach": instagram_data.reach,
                        "impressions": instagram_data.impressions,
                        "profile_views": instagram_data.profile_views,
                        "website_clicks": instagram_data.website_clicks,
                        "likes": instagram_data.likes,
                        "comments": instagram_data.comments,
                        "saves": instagram_data.saves,
                        "engagement_rate": instagram_data.engagement_rate,
                        "date_collected": instagram_data.date_collected.isoformat()
                    }
            except Exception as e:
                logger.error(f"Instagram analytics error: {str(e)}")

        return results

    def get_analytics_summary(self, linkedin_urn: str = None, twitter_username: str = None,
                            instagram_business_id: str = None) -> Dict:
        """Get summary analytics across all platforms"""
        all_analytics = self.get_all_analytics(linkedin_urn, twitter_username, instagram_business_id)

        total_followers = 0
        total_engagement = 0
        platforms_count = 0

        for platform, data in all_analytics.items():
            total_followers += data.get("followers", 0)
            total_engagement += data.get("engagement_rate", 0)
            platforms_count += 1

        avg_engagement_rate = total_engagement / platforms_count if platforms_count > 0 else 0

        return {
            "total_followers": total_followers,
            "average_engagement_rate": round(avg_engagement_rate, 2),
            "platforms_connected": platforms_count,
            "platforms": list(all_analytics.keys()),
            "last_updated": datetime.now().isoformat(),
            "detailed_analytics": all_analytics
        }