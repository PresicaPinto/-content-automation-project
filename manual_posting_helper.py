#!/usr/bin/env python3
"""
Manual Posting Helper - Safe and controlled posting
This helps you post content manually without API risks
"""

import json
import os
from datetime import datetime
from pathlib import Path
import subprocess

class ManualPostingHelper:
    """Helper for manual content posting"""

    def __init__(self):
        self.outputs_dir = Path('outputs')
        self.content_queue = []

    def load_content_calendar(self):
        """Load content calendar"""
        try:
            with open(self.outputs_dir / 'content_calendar.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ No content calendar found. Generate content first!")
            return []

    def load_twitter_calendar(self):
        """Load Twitter calendar"""
        try:
            with open(self.outputs_dir / 'twitter_calendar.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ No Twitter calendar found. Generate Twitter content first!")
            return []

    def get_todays_posts(self):
        """Get posts scheduled for today"""
        today = datetime.now().strftime('%Y-%m-%d')
        all_posts = self.load_content_calendar()

        todays_posts = [post for post in all_posts if post['publish_date'] == today]
        return todays_posts

    def get_todays_twitter(self):
        """Get Twitter threads for today"""
        today = datetime.now().strftime('%Y-%m-%d')
        all_twitter = self.load_twitter_calendar()

        todays_twitter = [thread for thread in all_twitter if thread['publish_date'] == today]
        return todays_twitter

    def show_posting_queue(self):
        """Show what needs to be posted today"""
        print("\n" + "="*60)
        print("📅 TODAY'S POSTING QUEUE")
        print("="*60)

        # LinkedIn posts
        linkedin_posts = self.get_todays_posts()
        if linkedin_posts:
            print(f"\n📱 LINKEDIN ({len(linkedin_posts)} posts):")
            for i, post in enumerate(linkedin_posts, 1):
                print(f"\n{i}. {post['topic']}")
                print(f"   🕐 Best time: 9:00 AM")
                print(f"   📝 Length: {len(post['content'])} characters")
                print(f"   📊 Status: Ready to post")

        # Twitter threads
        twitter_threads = self.get_todays_twitter()
        if twitter_threads:
            print(f"\n🐦 TWITTER ({len(twitter_threads)} threads):")
            for i, thread in enumerate(twitter_threads, 1):
                print(f"\n{i}. {thread['topic']}")
                print(f"   🕐 Best time: 2:00 PM")
                print(f"   📝 Tweets: {len(thread['tweets'])}")
                print(f"   📊 Status: Ready to post")

        if not linkedin_posts and not twitter_threads:
            print("\n✅ No posts scheduled for today!")
            print("🎯 Generate more content to keep your queue full")

        print("\n" + "="*60)

    def get_next_post_to_copy(self, platform='linkedin'):
        """Get the next post content ready for copying"""
        if platform == 'linkedin':
            posts = self.get_todays_posts()
            if posts:
                return posts[0]  # Return first post for today
        elif platform == 'twitter':
            threads = self.get_todays_twitter()
            if threads:
                return threads[0]  # Return first thread for today
        return None

    def copy_post_to_clipboard(self, platform='linkedin'):
        """Copy post content to clipboard"""
        try:
            import pyperclip

            post = self.get_next_post_to_copy(platform)
            if not post:
                print(f"❌ No {platform} post ready for today")
                return

            if platform == 'linkedin':
                content = post['content']
                print(f"\n📱 LinkedIn Post: {post['topic']}")
                print("-" * 40)
                print(content)
                print("-" * 40)
                pyperclip.copy(content)
                print("✅ Content copied to clipboard!")
                print("📌 Now go to LinkedIn and paste")

            elif platform == 'twitter':
                print(f"\n🐦 Twitter Thread: {post['topic']}")
                print("-" * 40)
                for i, tweet in enumerate(post['tweets'], 1):
                    print(f"Tweet {i}: {tweet}")
                    print()
                print("-" * 40)
                pyperclip.copy(post['tweets'][0])  # Copy first tweet
                print("✅ First tweet copied to clipboard!")
                print("📌 Post tweets in order on Twitter")

        except ImportError:
            print("❌ pyperclip not installed. Install with: pip install pyperclip")
            self.show_post_content(platform)

    def show_post_content(self, platform='linkedin'):
        """Show post content without copying to clipboard"""
        post = self.get_next_post_to_copy(platform)
        if not post:
            print(f"❌ No {platform} post ready for today")
            return

        print(f"\n📱 {platform.upper()} Post: {post['topic']}")
        print("=" * 50)

        if platform == 'linkedin':
            print(post['content'])
        elif platform == 'twitter':
            for i, tweet in enumerate(post['tweets'], 1):
                print(f"\nTweet {i}/{len(post['tweets'])}:")
                print(tweet)

        print("\n" + "=" * 50)
        print("📋 Copy the content above manually")

    def mark_post_as_posted(self, platform, post_index=0):
        """Mark a post as posted (for tracking)"""
        # This would update a tracking file
        # For now, just print confirmation
        print(f"✅ {platform.upper()} post marked as posted")

    def show_posting_schedule(self):
        """Show optimal posting schedule"""
        print("\n📅 OPTIMAL POSTING SCHEDULE:")
        print("="*40)
        print("🌅 MORNING (9:00 AM)")
        print("   • LinkedIn post")
        print("   • Professional audience")
        print("   • Business hours engagement")

        print("\n🌆 AFTERNOON (2:00 PM)")
        print("   • Twitter thread")
        print("   • High engagement time")
        print("   • Mobile users active")

        print("\n📊 BEST PRACTICES:")
        print("   • Post 30 minutes before optimal time")
        print("   • Engage with comments immediately")
        print("   • Use relevant hashtags")
        print("   • Add personal touch to AI content")

def main():
    """Main posting helper interface"""
    helper = ManualPostingHelper()

    while True:
        print("\n🎯 MANUAL POSTING HELPER")
        print("="*30)
        print("1. Show today's posting queue")
        print("2. Copy next LinkedIn post")
        print("3. Copy next Twitter thread")
        print("4. Show posting schedule")
        print("5. Generate more content")
        print("6. Exit")

        choice = input("\nSelect option (1-6): ").strip()

        if choice == '1':
            helper.show_posting_queue()

        elif choice == '2':
            helper.copy_post_to_clipboard('linkedin')

        elif choice == '3':
            helper.copy_post_to_clipboard('twitter')

        elif choice == '4':
            helper.show_posting_schedule()

        elif choice == '5':
            print("\n🚀 Generating 3 new posts...")
            result = subprocess.run(['python3', 'main.py', 'linkedin_batch', '3'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Content generated successfully!")
            else:
                print("❌ Error generating content")

        elif choice == '6':
            print("\n👋 Happy posting!")
            break

        else:
            print("❌ Invalid option. Try again.")

if __name__ == "__main__":
    main()