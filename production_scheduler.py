import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from dataclasses import dataclass
from scheduler import SocialMediaScheduler
from metrics_tracker import MetricsTracker

@dataclass
class ScheduledPost:
    id: str
    platform: str
    content: str
    scheduled_time: datetime
    profile_id: str
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, scheduled, failed, posted
    post_metadata: dict = None

class ProductionScheduler:
    """
    Production-ready scheduling service that runs continuously in the background.
    Handles failed posts, retry logic, and rate limiting.
    """

    def __init__(self, buffer_access_token: str):
        self.buffer_token = buffer_access_token
        self.scheduler = SocialMediaScheduler(buffer_access_token)
        self.metrics_tracker = MetricsTracker()

        # Configuration
        self.check_interval = 60  # Check every minute
        self.rate_limits = {
            'linkedin': {'posts_per_hour': 10, 'cooldown_minutes': 6},
            'twitter': {'posts_per_hour': 30, 'cooldown_minutes': 2}
        }

        # State tracking
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.post_history: List[dict] = []
        self.last_post_times: Dict[str, datetime] = {}

        # Threading
        self.running = False
        self.scheduler_thread = None

        # Logging
        self.logger = logging.getLogger(__name__)

    def add_scheduled_post(self, post: ScheduledPost) -> bool:
        """Add a post to the scheduling queue"""
        try:
            self.scheduled_posts[post.id] = post
            self.logger.info(f"Added post {post.id} to queue - {post.platform} at {post.scheduled_time}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding scheduled post: {e}")
            return False

    def load_posts_from_calendar(self, calendar_file: str, profile_ids: dict):
        """Load posts from content calendar files"""
        try:
            with open(calendar_file, 'r') as f:
                calendar = json.load(f)

            platform = calendar_file.split('_')[0]  # linkedin or twitter

            for item in calendar:
                post_id = f"{platform}_{item['post_number']}_{int(time.time())}"

                if platform == 'linkedin':
                    content = item['content']
                    profile_id = profile_ids.get('linkedin')
                else:  # twitter
                    # Handle twitter threads - schedule first tweet
                    content = item['tweets'][0] if item.get('tweets') else item.get('content', '')
                    profile_id = profile_ids.get('twitter')

                if not profile_id:
                    self.logger.error(f"No profile ID found for {platform}")
                    continue

                scheduled_time = datetime.strptime(item['publish_date'], '%Y-%m-%d')
                scheduled_time = scheduled_time.replace(hour=9, minute=0)  # Default to 9 AM

                post = ScheduledPost(
                    id=post_id,
                    platform=platform,
                    content=content,
                    scheduled_time=scheduled_time,
                    profile_id=profile_id,
                    post_metadata=item
                )

                self.add_scheduled_post(post)

            self.logger.info(f"Loaded {len(calendar)} posts from {calendar_file}")

        except Exception as e:
            self.logger.error(f"Error loading calendar {calendar_file}: {e}")

    def check_rate_limit(self, platform: str) -> bool:
        """Check if we're within rate limits for a platform"""
        now = datetime.now()
        last_post = self.last_post_times.get(platform)

        if not last_post:
            return True

        cooldown = self.rate_limits[platform]['cooldown_minutes']
        time_since_last = (now - last_post).total_seconds() / 60

        return time_since_last >= cooldown

    def post_to_platform(self, post: ScheduledPost) -> bool:
        """Post content to the platform"""
        try:
            if not self.check_rate_limit(post.platform):
                self.logger.warning(f"Rate limit exceeded for {post.platform}, skipping post {post.id}")
                return False

            # Schedule the post
            result = self.scheduler.schedule_post(
                profile_id=post.profile_id,
                text=post.content,
                scheduled_at=post.scheduled_time
            )

            if result.get('success') or result.get('id'):
                post.status = "posted"
                self.last_post_times[post.platform] = datetime.now()

                # Log to metrics
                self.metrics_tracker.log_metrics(
                    platform=post.platform,
                    post_number=post.post_metadata.get('post_number', 0),
                    topic=post.post_metadata.get('topic', 'Unknown'),
                    views=0,  # Will be updated later
                    likes=0,
                    comments=0,
                    shares=0
                )

                self.logger.info(f"Successfully posted {post.id} to {post.platform}")
                return True
            else:
                error = result.get('error', 'Unknown error')
                self.logger.error(f"Failed to post {post.id}: {error}")
                return False

        except Exception as e:
            self.logger.error(f"Error posting {post.id}: {e}")
            return False

    def process_pending_posts(self):
        """Process all pending posts that are ready to be posted"""
        now = datetime.now()
        posts_to_process = []

        # Find posts ready to be posted
        for post_id, post in self.scheduled_posts.items():
            if post.status == "pending" and post.scheduled_time <= now:
                posts_to_process.append(post)

        # Process each post
        for post in posts_to_process:
            self.logger.info(f"Processing post {post.id} for {post.platform}")

            success = self.post_to_platform(post)

            if success:
                post.status = "posted"
                self.post_history.append({
                    'post_id': post.id,
                    'platform': post.platform,
                    'posted_at': datetime.now().isoformat(),
                    'status': 'success'
                })
            else:
                post.retry_count += 1
                if post.retry_count >= post.max_retries:
                    post.status = "failed"
                    self.post_history.append({
                        'post_id': post.id,
                        'platform': post.platform,
                        'posted_at': datetime.now().isoformat(),
                        'status': 'failed',
                        'retry_count': post.retry_count
                    })
                    self.logger.error(f"Post {post.id} failed after {post.retry_count} retries")
                else:
                    # Schedule retry for 1 hour later
                    post.scheduled_time = datetime.now() + timedelta(hours=1)
                    self.logger.warning(f"Post {post.id} failed, scheduling retry {post.retry_count}/{post.max_retries}")

    def save_state(self):
        """Save current state to file for persistence"""
        state = {
            'scheduled_posts': {pid: {
                'id': p.id,
                'platform': p.platform,
                'content': p.content,
                'scheduled_time': p.scheduled_time.isoformat(),
                'profile_id': p.profile_id,
                'retry_count': p.retry_count,
                'status': p.status,
                'post_metadata': p.post_metadata
            } for pid, p in self.scheduled_posts.items()},
            'post_history': self.post_history,
            'last_post_times': {k: v.isoformat() for k, v in self.last_post_times.items()}
        }

        os.makedirs('outputs', exist_ok=True)
        with open('outputs/scheduler_state.json', 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """Load state from file"""
        try:
            with open('outputs/scheduler_state.json', 'r') as f:
                state = json.load(f)

            # Restore scheduled posts
            for pid, post_data in state.get('scheduled_posts', {}).items():
                post = ScheduledPost(
                    id=post_data['id'],
                    platform=post_data['platform'],
                    content=post_data['content'],
                    scheduled_time=datetime.fromisoformat(post_data['scheduled_time']),
                    profile_id=post_data['profile_id'],
                    retry_count=post_data['retry_count'],
                    status=post_data['status'],
                    post_metadata=post_data.get('post_metadata')
                )
                self.scheduled_posts[pid] = post

            # Restore other state
            self.post_history = state.get('post_history', [])
            self.last_post_times = {
                k: datetime.fromisoformat(v)
                for k, v in state.get('last_post_times', {}).items()
            }

            self.logger.info(f"Loaded {len(self.scheduled_posts)} scheduled posts from state")

        except FileNotFoundError:
            self.logger.info("No existing state file found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")

    def scheduler_loop(self):
        """Main scheduler loop that runs continuously"""
        self.logger.info("Production scheduler started")

        while self.running:
            try:
                # Process pending posts
                self.process_pending_posts()

                # Save state periodically
                self.save_state()

                # Wait before next check
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(self.check_interval)

    def start(self):
        """Start the scheduler service"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return

        # Load existing state
        self.load_state()

        # Start scheduler thread
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        self.logger.info("Production scheduler service started")

    def stop(self):
        """Stop the scheduler service"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)

        # Save final state
        self.save_state()

        self.logger.info("Production scheduler service stopped")

    def get_status(self) -> dict:
        """Get current scheduler status"""
        pending = len([p for p in self.scheduled_posts.values() if p.status == "pending"])
        posted = len([p for p in self.scheduled_posts.values() if p.status == "posted"])
        failed = len([p for p in self.scheduled_posts.values() if p.status == "failed"])

        return {
            'running': self.running,
            'total_posts': len(self.scheduled_posts),
            'pending_posts': pending,
            'posted_posts': posted,
            'failed_posts': failed,
            'last_post_times': {k: v.isoformat() for k, v in self.last_post_times.items()}
        }

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get configuration
    BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
    LINKEDIN_PROFILE_ID = os.getenv("LINKEDIN_PROFILE_ID")
    TWITTER_PROFILE_ID = os.getenv("TWITTER_PROFILE_ID")

    if not all([BUFFER_ACCESS_TOKEN, LINKEDIN_PROFILE_ID, TWITTER_PROFILE_ID]):
        print("Missing required environment variables:")
        print("BUFFER_ACCESS_TOKEN, LINKEDIN_PROFILE_ID, TWITTER_PROFILE_ID")
        exit(1)

    # Create and start scheduler
    scheduler = ProductionScheduler(BUFFER_ACCESS_TOKEN)

    # Load existing content calendars
    profile_ids = {
        'linkedin': LINKEDIN_PROFILE_ID,
        'twitter': TWITTER_PROFILE_ID
    }

    if os.path.exists('outputs/content_calendar.json'):
        scheduler.load_posts_from_calendar('outputs/content_calendar.json', profile_ids)

    if os.path.exists('outputs/twitter_calendar.json'):
        scheduler.load_posts_from_calendar('outputs/twitter_calendar.json', profile_ids)

    try:
        scheduler.start()
        print("Production scheduler is running. Press Ctrl+C to stop.")

        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")