#!/usr/bin/env python3
"""
Real-time Analytics Module
Enhances LinkedIn and Twitter integration with real-time data streaming and analysis
"""

import asyncio
import websockets
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import sqlite3
import logging
from pathlib import Path

# Import existing APIs
from linkedin_real_api import linkedin_real_api
from twitter_real_api import twitter_real_api
from social_media_analytics import SocialMediaAnalyticsManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealTimeMetrics:
    """Real-time metrics data structure"""
    platform: str
    metric_type: str
    value: float
    timestamp: datetime
    change_percent: float = 0.0
    trend: str = "stable"  # up, down, stable

    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class RealTimeAnalyticsEngine:
    """Real-time analytics engine for social media data"""

    def __init__(self):
        self.is_running = False
        self.update_interval = 60  # seconds
        self.subscribers = []
        self.metrics_history = []
        self.db_path = 'data/realtime_metrics.db'
        self.last_metrics = {}
        self.alert_thresholds = {
            'engagement_spike': 50.0,  # 50% increase
            'follower_drop': -10.0,    # 10% decrease
            'viral_threshold': 1000    # 1000+ impressions
        }

        # Initialize database
        self.init_database()

        # Setup analytics managers
        self.analytics_manager = SocialMediaAnalyticsManager()

    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        Path('data').mkdir(exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS real_time_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    change_percent REAL DEFAULT 0,
                    trend TEXT DEFAULT 'stable',
                    timestamp DATETIME NOT NULL,
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS metrics_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    threshold_value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS analytics_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    snapshot_data TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_metrics_platform_time
                ON real_time_metrics(platform, timestamp);

                CREATE INDEX IF NOT EXISTS idx_alerts_platform_time
                ON metrics_alerts(platform, timestamp);
            ''')

    async def start_real_time_monitoring(self, platforms: List[str], entities: Dict[str, str]):
        """Start real-time monitoring for specified platforms and entities"""
        self.is_running = True
        logger.info(f"Starting real-time monitoring for platforms: {platforms}")

        while self.is_running:
            try:
                # Collect metrics from all platforms
                tasks = []
                for platform in platforms:
                    if platform == 'linkedin' and 'linkedin' in entities:
                        tasks.append(self.collect_linkedin_metrics(entities['linkedin']))
                    elif platform == 'twitter' and 'twitter' in entities:
                        tasks.append(self.collect_twitter_metrics(entities['twitter']))

                # Execute tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results and notify subscribers
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Error collecting metrics: {result}")
                    elif result:
                        await self.process_new_metrics(result)

                # Wait for next update
                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in real-time monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error

    async def collect_linkedin_metrics(self, company_id: str) -> List[RealTimeMetrics]:
        """Collect real-time metrics from LinkedIn"""
        try:
            # Get current analytics
            analytics = linkedin_real_api.get_company_analytics(company_id)

            metrics = []
            now = datetime.now()

            # Process different metrics
            metric_mapping = {
                'followers': ('followers_count', analytics.get('followers', 0)),
                'engagement': ('engagement_rate', analytics.get('engagement', 0)),
                'impressions': ('impressions_count', analytics.get('impressions', 0)),
                'posts': ('posts_count', analytics.get('posts', 0)),
                'reach': ('reach_count', analytics.get('reach', 0))
            }

            for metric_type, (metric_name, value) in metric_mapping.items():
                # Calculate change from previous value
                last_value = self.last_metrics.get(f'linkedin_{metric_type}', 0)
                change_percent = self.calculate_change_percent(last_value, value)
                trend = self.determine_trend(change_percent)

                # Create metric object
                metric = RealTimeMetrics(
                    platform='linkedin',
                    metric_type=metric_type,
                    value=float(value),
                    timestamp=now,
                    change_percent=change_percent,
                    trend=trend
                )

                metrics.append(metric)
                self.last_metrics[f'linkedin_{metric_type}'] = value

                # Check for alerts
                await self.check_for_alerts(metric)

            # Store in database
            self.store_metrics(metrics, analytics)

            return metrics

        except Exception as e:
            logger.error(f"Error collecting LinkedIn metrics: {e}")
            return []

    async def collect_twitter_metrics(self, username: str) -> List[RealTimeMetrics]:
        """Collect real-time metrics from Twitter"""
        try:
            # Get current analytics
            analytics = twitter_real_api.get_user_analytics(username)

            metrics = []
            now = datetime.now()

            # Process different metrics
            metric_mapping = {
                'followers': ('followers_count', analytics.get('followers', 0)),
                'following': ('following_count', analytics.get('following', 0)),
                'tweets': ('tweets_count', analytics.get('tweets', 0)),
                'engagement': ('engagement_rate', analytics.get('engagement_rate', 0)),
                'impressions': ('tweet_impressions', analytics.get('tweet_impressions', 0)),
                'likes': ('tweet_likes', analytics.get('tweet_likes', 0)),
                'retweets': ('tweet_retweets', analytics.get('tweet_retweets', 0))
            }

            for metric_type, (metric_name, value) in metric_mapping.items():
                # Calculate change from previous value
                last_value = self.last_metrics.get(f'twitter_{metric_type}', 0)
                change_percent = self.calculate_change_percent(last_value, value)
                trend = self.determine_trend(change_percent)

                # Create metric object
                metric = RealTimeMetrics(
                    platform='twitter',
                    metric_type=metric_type,
                    value=float(value),
                    timestamp=now,
                    change_percent=change_percent,
                    trend=trend
                )

                metrics.append(metric)
                self.last_metrics[f'twitter_{metric_type}'] = value

                # Check for alerts
                await self.check_for_alerts(metric)

            # Store in database
            self.store_metrics(metrics, analytics)

            return metrics

        except Exception as e:
            logger.error(f"Error collecting Twitter metrics: {e}")
            return []

    def calculate_change_percent(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 0.0
        return round(((new_value - old_value) / old_value) * 100, 2)

    def determine_trend(self, change_percent: float) -> str:
        """Determine trend based on percentage change"""
        if change_percent > 5:
            return "up"
        elif change_percent < -5:
            return "down"
        else:
            return "stable"

    async def check_for_alerts(self, metric: RealTimeMetrics):
        """Check if metric triggers any alerts"""
        try:
            # Engagement spike alert
            if metric.metric_type == 'engagement' and metric.change_percent > self.alert_thresholds['engagement_spike']:
                await self.create_alert(
                    platform=metric.platform,
                    alert_type='engagement_spike',
                    message=f"Engagement spiked by {metric.change_percent}%!",
                    metric_value=metric.value,
                    threshold_value=self.alert_thresholds['engagement_spike']
                )

            # Follower drop alert
            if metric.metric_type == 'followers' and metric.change_percent < self.alert_thresholds['follower_drop']:
                await self.create_alert(
                    platform=metric.platform,
                    alert_type='follower_drop',
                    message=f"Followers decreased by {abs(metric.change_percent)}%",
                    metric_value=metric.value,
                    threshold_value=self.alert_thresholds['follower_drop']
                )

            # Viral content alert
            if metric.metric_type == 'impressions' and metric.value > self.alert_thresholds['viral_threshold']:
                await self.create_alert(
                    platform=metric.platform,
                    alert_type='viral_content',
                    message=f"Content going viral with {int(metric.value)} impressions!",
                    metric_value=metric.value,
                    threshold_value=self.alert_thresholds['viral_threshold']
                )

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    async def create_alert(self, platform: str, alert_type: str, message: str,
                          metric_value: float, threshold_value: float):
        """Create an alert in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO metrics_alerts
                    (platform, alert_type, message, metric_value, threshold_value, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (platform, alert_type, message, metric_value, threshold_value, datetime.now()))

            # Notify subscribers
            alert_data = {
                'type': 'alert',
                'platform': platform,
                'alert_type': alert_type,
                'message': message,
                'metric_value': metric_value,
                'threshold_value': threshold_value,
                'timestamp': datetime.now().isoformat()
            }

            await self.notify_subscribers(alert_data)
            logger.info(f"Alert created: {message}")

        except Exception as e:
            logger.error(f"Error creating alert: {e}")

    def store_metrics(self, metrics: List[RealTimeMetrics], raw_data: Dict):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for metric in metrics:
                    conn.execute('''
                        INSERT INTO real_time_metrics
                        (platform, metric_type, value, change_percent, trend, timestamp, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        metric.platform,
                        metric.metric_type,
                        metric.value,
                        metric.change_percent,
                        metric.trend,
                        metric.timestamp,
                        json.dumps(raw_data)
                    ))

            # Store snapshot
            self.store_snapshot(raw_data)

        except Exception as e:
            logger.error(f"Error storing metrics: {e}")

    def store_snapshot(self, raw_data: Dict):
        """Store complete analytics snapshot"""
        try:
            platform = raw_data.get('platform', 'unknown')
            entity_id = raw_data.get('company_id') or raw_data.get('username') or 'unknown'

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO analytics_snapshots
                    (platform, entity_id, snapshot_data, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (platform, entity_id, json.dumps(raw_data), datetime.now()))

        except Exception as e:
            logger.error(f"Error storing snapshot: {e}")

    async def process_new_metrics(self, metrics: List[RealTimeMetrics]):
        """Process new metrics and notify subscribers"""
        for metric in metrics:
            self.metrics_history.append(metric)

            # Keep only last 1000 metrics in memory
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

        # Notify subscribers
        await self.notify_subscribers({
            'type': 'metrics_update',
            'metrics': [m.to_dict() for m in metrics],
            'timestamp': datetime.now().isoformat()
        })

    async def notify_subscribers(self, data: Dict):
        """Notify all WebSocket subscribers"""
        if self.subscribers:
            message = json.dumps(data)
            # Create tasks for all subscribers
            tasks = [websocket.send(message) for websocket in self.subscribers]
            # Execute all notifications concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

    def subscribe(self, websocket):
        """Subscribe a WebSocket client to real-time updates"""
        self.subscribers.append(websocket)
        logger.info(f"New subscriber. Total: {len(self.subscribers)}")

    def unsubscribe(self, websocket):
        """Unsubscribe a WebSocket client"""
        if websocket in self.subscribers:
            self.subscribers.remove(websocket)
            logger.info(f"Subscriber removed. Total: {len(self.subscribers)}")

    def get_historical_metrics(self, platform: str, metric_type: str,
                              hours: int = 24) -> List[Dict]:
        """Get historical metrics for a platform and metric type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM real_time_metrics
                    WHERE platform = ? AND metric_type = ?
                    AND timestamp >= datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                '''.format(hours), (platform, metric_type))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting historical metrics: {e}")
            return []

    def get_recent_alerts(self, platform: str = None, limit: int = 10) -> List[Dict]:
        """Get recent alerts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                query = '''
                    SELECT * FROM metrics_alerts
                    WHERE 1=1
                '''
                params = []

                if platform:
                    query += ' AND platform = ?'
                    params.append(platform)

                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)

                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []

    def get_analytics_summary(self, platform: str = None) -> Dict:
        """Get comprehensive analytics summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get latest metrics per platform
                query = '''
                    SELECT platform, metric_type, value, trend, change_percent, timestamp
                    FROM real_time_metrics r1
                    WHERE timestamp = (
                        SELECT MAX(timestamp)
                        FROM real_time_metrics r2
                        WHERE r2.platform = r1.platform AND r2.metric_type = r1.metric_type
                    )
                '''
                params = []

                if platform:
                    query += ' AND platform = ?'
                    params.append(platform)

                cursor = conn.execute(query, params)
                latest_metrics = [dict(row) for row in cursor.fetchall()]

                # Organize by platform
                summary = {}
                for metric in latest_metrics:
                    plat = metric['platform']
                    if plat not in summary:
                        summary[plat] = {}
                    summary[plat][metric['metric_type']] = metric

                return summary

        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}

    def stop(self):
        """Stop real-time monitoring"""
        self.is_running = False
        logger.info("Real-time monitoring stopped")

# WebSocket server for real-time updates
async def websocket_handler(websocket, path, analytics_engine: RealTimeAnalyticsEngine):
    """Handle WebSocket connections for real-time updates"""
    logger.info(f"New WebSocket connection from {websocket.remote_address}")

    # Subscribe to updates
    analytics_engine.subscribe(websocket)

    try:
        # Send current analytics summary
        summary = analytics_engine.get_analytics_summary()
        await websocket.send(json.dumps({
            'type': 'initial_summary',
            'data': summary,
            'timestamp': datetime.now().isoformat()
        }))

        # Keep connection alive
        async for message in websocket:
            try:
                data = json.loads(message)
                # Handle client requests if needed
                if data.get('type') == 'get_history':
                    platform = data.get('platform')
                    metric = data.get('metric')
                    hours = data.get('hours', 24)
                    history = analytics_engine.get_historical_metrics(platform, metric, hours)
                    await websocket.send(json.dumps({
                        'type': 'history_data',
                        'data': history,
                        'timestamp': datetime.now().isoformat()
                    }))

            except json.JSONDecodeError:
                logger.error("Invalid JSON received from client")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")

    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket connection closed")
    finally:
        # Unsubscribe when connection closes
        analytics_engine.unsubscribe(websocket)

async def start_websocket_server(analytics_engine: RealTimeAnalyticsEngine,
                                host: str = 'localhost', port: int = 8765):
    """Start WebSocket server for real-time updates"""
    logger.info(f"Starting WebSocket server on {host}:{port}")

    # Create partial function to pass analytics_engine to handler
    import functools
    handler = functools.partial(websocket_handler, analytics_engine=analytics_engine)

    async with websockets.serve(handler, host, port):
        logger.info("WebSocket server started successfully")
        await asyncio.Future()  # Run forever

# Global instance
real_time_engine = RealTimeAnalyticsEngine()

def start_real_time_analytics(platforms: List[str], entities: Dict[str, str]):
    """Start real-time analytics monitoring"""
    # Setup API credentials if available
    # Note: In production, these should come from environment variables
    # linkedin_real_api.setup_with_credentials(...)
    # twitter_real_api.setup_with_credentials(...)

    # Start monitoring in background
    async def run_monitoring():
        asyncio.create_task(real_time_engine.start_real_time_monitoring(platforms, entities))
        await start_websocket_server(real_time_engine)

    # Run in new event loop
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_monitoring())

    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()

    logger.info("Real-time analytics started in background thread")
    return real_time_engine

if __name__ == "__main__":
    # Example usage
    platforms = ['twitter']
    entities = {'twitter': 'elonmusk'}  # Example Twitter username

    engine = start_real_time_analytics(platforms, entities)

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping real-time analytics...")
        engine.stop()