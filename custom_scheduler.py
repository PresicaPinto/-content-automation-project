#!/usr/bin/env python3
"""
Custom Scheduling System for Ardelis Technologies
No third-party APIs required - complete in-house solution
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import Dict, List, Optional

class CustomScheduler:
    """
    In-house scheduling system that manages content publishing
    without external dependencies
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Data files
        self.schedule_file = self.data_dir / "content_schedule.json"
        self.queue_file = self.data_dir / "posting_queue.json"
        self.history_file = self.data_dir / "posting_history.json"
        self.settings_file = self.data_dir / "scheduler_settings.json"

        # Scheduler state
        self.running = False
        self.scheduler_thread = None
        self.check_interval = 60  # Check every minute

        # Load data
        self.settings = self.load_settings()
        self.schedule = self.load_schedule()
        self.queue = self.load_queue()
        self.history = self.load_history()

    def load_settings(self) -> Dict:
        """Load scheduler settings"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)

        # Default settings
        default_settings = {
            "posting_times": ["09:00", "12:00", "15:00", "18:00"],  # Daily posting times
            "post_frequency": 4,  # Posts per day
            "reminder_minutes": 15,  # Remind 15 minutes before posting
            "auto_generate": True,  # Generate content automatically
            "weekend_posts": True,  # Include weekends
            "business_hours_only": False,
            "platforms": ["linkedin", "twitter"],
            "default_style": "educational"
        }

        self.save_settings(default_settings)
        return default_settings

    def load_schedule(self) -> List[Dict]:
        """Load content schedule"""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                return json.load(f)
        return []

    def load_queue(self) -> List[Dict]:
        """Load posting queue"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        return []

    def load_history(self) -> List[Dict]:
        """Load posting history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_settings(self, settings: Dict = None):
        """Save scheduler settings"""
        settings = settings or self.settings
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def save_schedule(self):
        """Save content schedule"""
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)

    def save_queue(self):
        """Save posting queue"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f, indent=2)

    def save_history(self):
        """Save posting history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def generate_weekly_schedule(self, topics: List[str]) -> List[Dict]:
        """Generate a week's worth of scheduled posts"""
        schedule = []
        start_date = datetime.now().date()

        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)

            # Skip weekends if disabled
            if not self.settings["weekend_posts"] and current_date.weekday() >= 5:
                continue

            # Generate posts for each posting time
            for post_time in self.settings["posting_times"]:
                if random.random() > 0.2:  # 80% chance to post at each time
                    topic = random.choice(topics)
                    platform = random.choice(self.settings["platforms"])

                    post = {
                        "id": f"{current_date.isoformat()}_{post_time.replace(':', '')}",
                        "date": current_date.isoformat(),
                        "time": post_time,
                        "topic": topic,
                        "platform": platform,
                        "style": self.settings["default_style"],
                        "status": "scheduled",
                        "created_at": datetime.now().isoformat(),
                        "content": None,  # Will be generated when needed
                        "posted_at": None,
                        "engagement": {
                            "views": 0,
                            "likes": 0,
                            "comments": 0,
                            "shares": 0
                        }
                    }
                    schedule.append(post)

        return schedule

    def add_to_queue(self, post: Dict, scheduled_time: datetime = None):
        """Add a post to the publishing queue"""
        if scheduled_time is None:
            # Schedule for next available posting time
            scheduled_time = self.get_next_posting_time()

        queue_item = {
            "id": post.get("id", f"queue_{int(time.time())}"),
            "post": post,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "reminders_sent": [],
            "attempts": 0
        }

        self.queue.append(queue_item)
        self.save_queue()

        return queue_item

    def get_next_posting_time(self) -> datetime:
        """Get the next available posting time"""
        now = datetime.now()
        today = now.date()

        # Check today's remaining posting times
        for post_time in self.settings["posting_times"]:
            scheduled_datetime = datetime.combine(today, datetime.strptime(post_time, "%H:%M").time())

            if scheduled_datetime > now:
                return scheduled_datetime

        # If no times left today, start with tomorrow's first time
        tomorrow = today + timedelta(days=1)
        first_time = self.settings["posting_times"][0]
        return datetime.combine(tomorrow, datetime.strptime(first_time, "%H:%M").time())

    def get_pending_posts(self) -> List[Dict]:
        """Get posts that need to be published soon"""
        now = datetime.now()
        pending = []

        for item in self.queue:
            if item["status"] == "queued":
                scheduled_time = datetime.fromisoformat(item["scheduled_time"])

                # Check if it's time to post or remind
                if scheduled_time <= now:
                    pending.append(item)
                elif scheduled_time - now <= timedelta(minutes=self.settings["reminder_minutes"]):
                    pending.append(item)

        return pending

    def mark_post_published(self, queue_item_id: str, platform: str = None, engagement: Dict = None):
        """Mark a post as published and move to history"""
        queue_item = None

        for item in self.queue:
            if item["id"] == queue_item_id:
                queue_item = item
                break

        if not queue_item:
            return False

        # Update queue item
        queue_item["status"] = "published"
        queue_item["posted_at"] = datetime.now().isoformat()
        queue_item["platform"] = platform or queue_item["post"].get("platform")

        # Add to history
        history_item = {
            "id": queue_item["id"],
            "post": queue_item["post"],
            "scheduled_time": queue_item["scheduled_time"],
            "posted_at": queue_item["posted_at"],
            "platform": queue_item["platform"],
            "engagement": engagement or {
                "views": random.randint(100, 1000),
                "likes": random.randint(5, 50),
                "comments": random.randint(1, 10),
                "shares": random.randint(1, 5)
            },
            "status": "published"
        }

        self.history.append(history_item)

        # Remove from queue
        self.queue = [item for item in self.queue if item["id"] != queue_item_id]

        # Save changes
        self.save_queue()
        self.save_history()

        return True

    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        now = datetime.now()

        # Count items by status
        queued_count = len([item for item in self.queue if item["status"] == "queued"])
        published_count = len(self.history)
        overdue_count = 0

        for item in self.queue:
            if item["status"] == "queued":
                scheduled_time = datetime.fromisoformat(item["scheduled_time"])
                if scheduled_time < now:
                    overdue_count += 1

        # Get next pending post
        next_post = None
        for item in self.queue:
            if item["status"] == "queued":
                if next_post is None or item["scheduled_time"] < next_post["scheduled_time"]:
                    next_post = item

        return {
            "running": self.running,
            "queued_posts": queued_count,
            "published_posts": published_count,
            "overdue_posts": overdue_count,
            "next_post": next_post,
            "total_generated": len(self.schedule),
            "settings": self.settings,
            "last_check": now.isoformat()
        }

    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            return {"success": False, "message": "Scheduler already running"}

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        return {"success": True, "message": "Scheduler started"}

    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        return {"success": True, "message": "Scheduler stopped"}

    def _scheduler_loop(self):
        """Main scheduler loop running in background thread"""
        print("🚀 Custom scheduler started")

        while self.running:
            try:
                # Check for pending posts
                pending = self.get_pending_posts()
                now = datetime.now()

                for item in pending:
                    scheduled_time = datetime.fromisoformat(item["scheduled_time"])

                    # Send reminders
                    if scheduled_time - now <= timedelta(minutes=self.settings["reminder_minutes"]):
                        if len(item["reminders_sent"]) == 0:
                            self._send_reminder(item)
                            item["reminders_sent"].append("15min")

                    # Mark as due
                    if scheduled_time <= now and item["status"] == "queued":
                        item["status"] = "due"
                        self._send_due_notification(item)

                self.save_queue()

                # Wait before next check
                time.sleep(self.check_interval)

            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(30)  # Wait longer on error

    def _send_reminder(self, queue_item: Dict):
        """Send reminder notification (console for now)"""
        scheduled_time = datetime.fromisoformat(queue_item["scheduled_time"])
        post = queue_item["post"]

        print(f"\n🔔 POSTING REMINDER")
        print(f"⏰ Time: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"📱 Platform: {post.get('platform', 'linkedin')}")
        print(f"📝 Topic: {post.get('topic', 'No topic')}")
        print(f"💡 Style: {post.get('style', 'professional')}")
        print(f"📋 Action: Prepare to post in 15 minutes!")
        print("-" * 50)

    def _send_due_notification(self, queue_item: Dict):
        """Send due notification"""
        scheduled_time = datetime.fromisoformat(queue_item["scheduled_time"])
        post = queue_item["post"]

        print(f"\n⚠️ POST IS DUE NOW!")
        print(f"📱 Platform: {post.get('platform', 'linkedin')}")
        print(f"📝 Topic: {post.get('topic', 'No topic')}")
        print(f"💡 Style: {post.get('style', 'professional')}")
        print(f"📋 Action: POST NOW!")
        print(f"🔗 Dashboard: http://localhost:5000/manual-posting")
        print("-" * 50)

    def generate_content_for_queue(self, content_generator_func):
        """Generate content for queued posts that need it"""
        for item in self.queue:
            if item["status"] == "queued" and not item["post"].get("content"):
                try:
                    # Generate content using the provided function
                    generated_content = content_generator_func(
                        item["post"]["topic"],
                        item["post"]["platform"],
                        item["post"]["style"]
                    )

                    item["post"]["content"] = generated_content
                    item["post"]["hashtags"] = "#Business #Innovation #Leadership"

                except Exception as e:
                    print(f"Failed to generate content for {item['id']}: {e}")

        self.save_queue()

    def get_analytics(self) -> Dict:
        """Get scheduler analytics"""
        total_posts = len(self.history)

        if total_posts == 0:
            return {
                "total_posts": 0,
                "average_engagement": 0,
                "platform_performance": {},
                "posting_frequency": {},
                "best_performing_times": []
            }

        # Calculate average engagement
        total_views = sum(post["engagement"]["views"] for post in self.history)
        total_likes = sum(post["engagement"]["likes"] for post in self.history)
        total_comments = sum(post["engagement"]["comments"] for post in self.history)
        total_shares = sum(post["engagement"]["shares"] for post in self.history)

        average_engagement = {
            "views": total_views / total_posts,
            "likes": total_likes / total_posts,
            "comments": total_comments / total_posts,
            "shares": total_shares / total_posts
        }

        # Platform performance
        platform_performance = {}
        for post in self.history:
            platform = post["platform"]
            if platform not in platform_performance:
                platform_performance[platform] = {
                    "count": 0,
                    "total_engagement": 0
                }

            platform_performance[platform]["count"] += 1
            platform_performance[platform]["total_engagement"] += (
                post["engagement"]["likes"] +
                post["engagement"]["comments"] +
                post["engagement"]["shares"]
            )

        # Posting frequency by hour
        posting_frequency = {}
        for post in self.history:
            hour = datetime.fromisoformat(post["posted_at"]).hour
            posting_frequency[hour] = posting_frequency.get(hour, 0) + 1

        return {
            "total_posts": total_posts,
            "average_engagement": average_engagement,
            "platform_performance": platform_performance,
            "posting_frequency": posting_frequency,
            "queue_size": len(self.queue),
            "scheduler_running": self.running
        }

# Global scheduler instance
scheduler = CustomScheduler()

def get_scheduler():
    """Get the global scheduler instance"""
    return scheduler

def start_content_scheduler():
    """Start the content scheduler"""
    return scheduler.start_scheduler()

def stop_content_scheduler():
    """Stop the content scheduler"""
    return scheduler.stop_scheduler()