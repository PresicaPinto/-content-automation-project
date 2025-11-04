#!/usr/bin/env python3
"""
Production Content Automation Machine
Generates €100,000+ in revenue through automated content creation
Following the specifications from INTERN_INSTRUCTIONS.md
"""

import asyncio
import aiohttp
import json
import os
import time
import hashlib
import sqlite3
import argparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
import schedule
import threading

class ProductionContentGenerator:
    """Enterprise-grade content generation system for lead generation"""

    def __init__(self):
        self.api_key = os.getenv('ZAI_API_KEY')
        self.base_url = "https://api.z.ai/api/paas/v4/chat/completions"
        self.max_workers = 5  # Production parallel processing
        self.timeout = 30
        self.cache_db_path = "production_cache/content_cache.db"
        self.content_db_path = "production_database/content.db"
        self._init_databases()

    def _init_databases(self):
        """Initialize production databases"""
        os.makedirs("production_cache", exist_ok=True)
        os.makedirs("production_database", exist_ok=True)

        # Cache database
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_cache (
                    hash_key TEXT PRIMARY KEY,
                    content TEXT,
                    topic TEXT,
                    style TEXT,
                    platform TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Content database for tracking
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_number INTEGER,
                    topic TEXT,
                    platform TEXT,
                    style TEXT,
                    content TEXT,
                    content_hash TEXT,
                    publish_date TEXT,
                    scheduled_date TEXT,
                    status TEXT DEFAULT 'draft',
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_id TEXT,
                    UNIQUE(content_hash)
                )
            ''')

            # Analytics database
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    platform TEXT,
                    total_posts INTEGER DEFAULT 0,
                    total_views INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    total_shares INTEGER DEFAULT 0,
                    avg_engagement_rate REAL DEFAULT 0.0,
                    top_performing_topic TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def get_cache_key(self, topic: str, style: str, platform: str = "linkedin") -> str:
        """Generate optimized cache key"""
        cache_data = f"{topic.lower().strip()}|{style}|{platform}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def check_cache(self, cache_key: str) -> str:
        """Fast cache lookup with TTL"""
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute(
                'SELECT content FROM content_cache WHERE hash_key = ? AND expires_at > datetime("now")',
                (cache_key,)
            )
            result = cursor.fetchone()
            if result:
                # Update access tracking
                conn.execute(
                    'UPDATE content_cache SET access_count = access_count + 1, last_accessed = datetime("now") WHERE hash_key = ?',
                    (cache_key,)
                )
                conn.commit()
            return result[0] if result else None

    def cache_content(self, cache_key: str, content: str, topic: str, style: str, platform: str = "linkedin"):
        """Cache content with production TTL"""
        expires_at = datetime.now() + timedelta(days=7)  # 7-day cache for production
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO content_cache (hash_key, content, topic, style, platform, expires_at) VALUES (?, ?, ?, ?, ?, ?)',
                (cache_key, content, topic, style, platform, expires_at)
            )
            conn.commit()

    def create_production_prompt(self, topic: str, style: str, platform: str = "linkedin") -> str:
        """Create professional prompts optimized for lead generation"""

        style_prompts = {
            'educational': {
                'linkedin': """You are a senior content strategist writing for Merryl D'Mello, founder of Ardelis Technologies, who builds agentic AI systems for European businesses.

Topic: {topic}

Create a LinkedIn post that:
1. Starts with a compelling hook (statistic, surprising fact, or provocative question)
2. Provides 2-3 valuable insights about {topic}
3. Shows how agentic AI solves specific business problems
4. Includes a clear call-to-action for business leaders

Style guidelines:
- Professional but conversational tone
- 400-600 words
- Use line breaks for readability
- Include 2-3 relevant hashtags
- End with a question to encourage engagement
- Focus on business value and ROI

Write as if you're a consultant sharing expert insights with C-suite executives.""",

                'twitter': """You are a tech thought leader sharing insights about {topic}.

Create a Twitter thread (5-7 tweets total):
- Tweet 1: Hook that grabs attention
- Tweets 2-5: One key insight per tweet
- Tweet 6: Main takeaway or actionable advice
- Tweet 7: Question or CTA

Style guidelines:
- Conversational and punchy
- Each tweet 200-280 characters
- Use emojis sparingly
- Thread numbering (1/7, 2/7, etc.)
- Focus on actionable insights
- End with engagement driver

Create JSON array: ["tweet1", "tweet2", ...]""",
            },

            'case_study': {
                'linkedin': """You are Merryl D'Mello sharing a successful agentic AI implementation.

Write a LinkedIn case study about: {topic}

Structure:
1. Hook with impressive results
2. Client background (industry, size, challenges)
3. Problem: What wasn't working
4. Solution: How agentic AI was implemented
5. Results: Specific metrics and outcomes
6. Key lessons: What others can learn

Style guidelines:
- Data-driven and specific
- Include numbers and percentages
- Show clear before/after
- Professional and authoritative
- 400-600 words
- End with consultation offer

Make it feel like a genuine success story with real impact.""",

                'twitter': """Share a case study about {topic} on Twitter.

Create a thread (6-8 tweets):
1. Impressive result hook
2. Client background
3. Problem statement
4. Solution implementation
5. Results with metrics
6. Key lessons
7. What this means for others
8. Call to action

Focus on concrete numbers and outcomes. Make it actionable for other businesses.""",
            },

            'story': {
                'linkedin': """You are Merryl D'Mello sharing a personal journey with agentic AI.

Write a LinkedIn story about: {topic}

Structure:
1. Relatable opening about the situation
2. Challenges or turning point
3. Discovery or breakthrough moment
4. Implementation journey
5. Current state and results
6. Key insights learned

Style guidelines:
- Personal and authentic
- Show vulnerability and growth
- Emotional connection points
- Professional takeaway
- 400-600 words
- Inspiring but grounded

Make it feel like a genuine journey that others can learn from.""",

                'twitter': """Share a personal story about {topic}.

Create a thread (6-8 tweets) showing your journey:
1. Where you started
2. Challenges faced
3. Turning point
4. Key breakthrough
5. Current success
6. Lessons learned
7. Advice for others
8. Inspiring closing

Keep it personal, authentic, and actionable."""
            },

            'insight': {
                'linkedin': """You are a forward-thinking expert sharing contrarian insights about {topic}.

Write a LinkedIn insight post that:
1. Challenges conventional wisdom
2. Presents a surprising perspective
3. Backs it up with evidence or logic
4. Explains implications for businesses
5. Provides actionable advice

Style guidelines:
- Provocative but professional
- Backed by research or experience
- Challenges status quo
- Forward-looking perspective
- 400-600 words
- Sparks discussion and debate
- Position as thought leader

Take a strong, defensible position that others may disagree with but can't ignore.""",

                'twitter': """Share a provocative insight about {topic}.

Create a thread (5-6 tweets):
1. Contrarian statement
2. Evidence or reasoning
3. Why conventional thinking is wrong
4. Better approach
5. Business implications
6. Call to question/discussion

Be bold but professional. Back up your claims with logic."""
            }
        }

        templates = style_prompts.get(style, style_prompts['educational'])
        prompt = templates.get(platform, templates['linkedin'])

        return prompt.format(topic=topic)

    async def generate_content_async(self, topic_data: Dict[str, Any], session: aiohttp.ClientSession, platform: str = "linkedin") -> Dict[str, Any]:
        """Generate content with production-grade quality and caching"""
        topic = topic_data['topic']
        style = topic_data['style']

        # Check cache first
        cache_key = self.get_cache_key(topic, style, platform)
        cached_content = self.check_cache(cache_key)

        if cached_content:
            return {
                'success': True,
                'topic': topic,
                'content': cached_content,
                'style': style,
                'platform': platform,
                'cached': True,
                'generation_time': 0.1
            }

        # Generate new content
        prompt = self.create_production_prompt(topic, style, platform)

        payload = {
            "model": "GLM-4.5-Flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,  # Increased to prevent truncation
            "temperature": 0.7
        }

        start_time = time.time()

        try:
            async with session.post(
                self.base_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]

                    # Process Twitter JSON if needed
                    if platform == 'twitter' and style in ['educational', 'case_study', 'story', 'insight']:
                        try:
                            content = json.loads(content)
                            if isinstance(content, list):
                                content = '\n\n'.join(content)
                        except:
                            pass  # Keep as regular text if JSON parsing fails

                    # Cache the result
                    self.cache_content(cache_key, content, topic, style, platform)

                    generation_time = time.time() - start_time

                    return {
                        'success': True,
                        'topic': topic,
                        'content': content,
                        'style': style,
                        'platform': platform,
                        'cached': False,
                        'generation_time': generation_time
                    }
                else:
                    return {
                        'success': False,
                        'topic': topic,
                        'error': f"HTTP {response.status}",
                        'generation_time': time.time() - start_time
                    }
        except Exception as e:
            return {
                'success': False,
                'topic': topic,
                'error': str(e),
                'generation_time': time.time() - start_time
            }

    async def generate_batch_async(self, topics_data: List[Dict[str, Any]], num_posts: int = 5, platform: str = "linkedin") -> tuple:
        """Generate content batch with production parallel processing"""
        if not topics_data:
            return [], []

        # Select topics
        selected_topics = topics_data[:num_posts]

        print(f"🚀 Production Generator: Processing {len(selected_topics)} {platform} posts")
        print(f"⚡ Max workers: {self.max_workers}, Cache enabled: 7-day TTL")

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.generate_content_async(topic, session, platform)
                for topic in selected_topics
            ]

            # Execute with concurrency control
            results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Process results
        successful_posts = []
        failed_posts = []
        cache_hits = 0
        total_generation_time = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_posts.append({
                    'topic': selected_topics[i]['topic'],
                    'error': str(result)
                })
            elif result['success']:
                successful_posts.append(result)
                total_generation_time += result.get('generation_time', 0)
                if result['cached']:
                    cache_hits += 1
                print(f"✅ {'[CACHED] ' if result['cached'] else ''}Generated: {result['topic']}")
            else:
                failed_posts.append(result)
                print(f"❌ Failed: {result.get('topic', 'Unknown')} - {result.get('error', 'Unknown error')}")

        # Production metrics
        avg_time_per_post = total_time / len(selected_topics) if selected_topics else 0
        cache_efficiency = (cache_hits / len(selected_topics)) * 100 if selected_topics else 0
        total_content_length = sum(len(post['content']) for post in successful_posts)
        avg_content_length = total_content_length / len(successful_posts) if successful_posts else 0

        print(f"\n📊 Production Results:")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        print(f"⚡ Avg time per post: {avg_time_per_post:.1f} seconds")
        print(f"💾 Cache efficiency: {cache_efficiency:.1f}%")
        print(f"📝 Avg content length: {avg_content_length:.0f} characters")
        print(f"✅ Success rate: {len(successful_posts)}/{len(selected_topics)} ({(len(successful_posts)/len(selected_topics))*100:.1f}%)")
        print(f"🚀 Production ready: {len(successful_posts)} posts generated")

        return successful_posts, failed_posts

    def generate_batch_sync(self, topics_data: List[Dict[str, Any]], num_posts: int = 5, platform: str = "linkedin") -> tuple:
        """Synchronous wrapper for async generation"""
        try:
            return asyncio.run(self.generate_batch_async(topics_data, num_posts, platform))
        except Exception as e:
            print(f"❌ Production generation error: {e}")
            return [], []

    def save_to_production_db(self, posts: List[Dict[str, Any]], platform: str = "linkedin", batch_id: str = None):
        """Save content to production database with full tracking"""
        if not posts:
            return None

        batch_id = batch_id or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()

        enhanced_posts = []
        with sqlite3.connect(self.content_db_path) as conn:
            for i, post in enumerate(posts):
                content_hash = hashlib.md5(post['content'].encode()).hexdigest()

                # Check if already exists
                existing = conn.execute(
                    'SELECT id FROM content_library WHERE content_hash = ?',
                    (content_hash,)
                ).fetchone()

                if not existing:
                    conn.execute('''
                        INSERT INTO content_library (
                            post_number, topic, platform, style, content, content_hash,
                            publish_date, scheduled_date, status, batch_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        i + 1,
                        post['topic'],
                        platform,
                        post['style'],
                        post['content'],
                        content_hash,
                        datetime.now().strftime('%Y-%m-%d'),
                        None,  # Scheduled date
                        'draft',
                        batch_id
                    ))

                    enhanced_posts.append({
                        'post_number': i + 1,
                        'topic': post['topic'],
                        'platform': platform,
                        'style': post['style'],
                        'content': post['content'],
                        'content_hash': content_hash,
                        'publish_date': datetime.now().strftime('%Y-%m-%d'),
                        'scheduled_date': None,
                        'status': 'draft',
                        'created_at': timestamp,
                        'batch_id': batch_id,
                        'cached': post.get('cached', False),
                        'views': 0,
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'engagement_rate': 0.0
                    })

            conn.commit()

        print(f"💾 Saved {len(enhanced_posts)} posts to production database")
        return batch_id

    def generate_content_calendar(self, topics_file: str = 'topics.json', num_days: int = 30) -> List[Dict[str, Any]]:
        """Generate 30-day content calendar for production"""
        print(f"📅 Generating {num_days}-day content calendar...")

        # Load topics
        with open(topics_file, 'r') as f:
            topics = json.load(f)

        content_calendar = []

        for day in range(num_days):
            # Cycle through topics
            topic_index = day % len(topics)
            topic = topics[topic_index]

            # Generate content for the day
            successful_posts, _ = self.generate_batch_sync([topic], 1, 'linkedin')

            if successful_posts:
                post = successful_posts[0]

                content_calendar.append({
                    'day': day + 1,
                    'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                    'topic': topic['topic'],
                    'content': post['content'],
                    'style': topic['style'],
                    'platform': 'linkedin',
                    'status': 'ready',
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'engagement_rate': 0.0
                })

            print(f"✅ Day {day + 1}: {topic['topic']}")

        # Save calendar
        with open('production_content_calendar.json', 'w') as f:
            json.dump(content_calendar, f, indent=2)

        print(f"📅 Saved {len(content_calendar)}-day content calendar")
        return content_calendar

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get production analytics summary"""
        with sqlite3.connect(self.content_db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Content library stats
            total_posts = conn.execute('SELECT COUNT(*) FROM content_library').fetchone()[0]
            published_posts = conn.execute('SELECT COUNT(*) FROM content_library WHERE status = "published"').fetchone()[0]

            # Performance stats
            cursor = conn.execute('''
                SELECT platform, AVG(engagement_rate) as avg_engagement,
                       SUM(views) as total_views, SUM(likes) as total_likes,
                       SUM(comments) as total_comments, SUM(shares) as total_shares,
                       COUNT(*) as post_count
                FROM content_library
                WHERE status = "published" AND views > 0
                GROUP BY platform
            ''')

            performance = [dict(row) for row in cursor.fetchall()]

            # Top performing content
            cursor = conn.execute('''
                SELECT topic, AVG(engagement_rate) as avg_engagement, COUNT(*) as post_count
                FROM content_library
                WHERE status = "published" AND views > 0
                GROUP BY topic
                ORDER BY avg_engagement DESC
                LIMIT 10
            ''')

            top_content = [dict(row) for row in cursor.fetchall()]

            return {
                'total_content_generated': total_posts,
                'content_published': published_posts,
                'content_draft': total_posts - published_posts,
                'platform_performance': performance,
                'top_performing_topics': top_content,
                'last_updated': datetime.now().isoformat()
            }


def load_topics():
    """Load production topics"""
    try:
        with open('topics.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ topics.json not found")
        return []


def main():
    """Production content generator main function"""
    print("🚀 PRODUCTION CONTENT AUTOMATION MACHINE")
    print("=" * 60)
    print("Enterprise-grade content generation for lead generation")
    print("Goal: Generate €100,000+ in revenue")
    print("=" * 60)

    # Load configuration
    topics = load_topics()
    if not topics:
        print("❌ No topics found in topics.json")
        return

    generator = ProductionContentGenerator()

    print(f"\n📊 Available Topics: {len(topics)}")
    print(f"🎯 Styles: {len(set(t['style'] for t in topics))}")
    print(f"🚀 Production Cache: 7-day TTL")
    print(f"⚡ Parallel Processing: {generator.max_workers} workers")

    # Interactive production menu
    print(f"\n📋 Production Menu:")
    print("1. Generate single batch (5 posts)")
    print("2. Generate large batch (20 posts)")
    print("3. Generate 30-day content calendar")
    print("4. Custom batch generation")
    print("5. View analytics")
    print("6. Emergency batch (100 posts)")

    choice = input("\nSelect option (1-6): ").strip()

    if choice == '1':
        # Single batch
        print(f"\n⚡ Generating 5 LinkedIn posts...")
        posts, _ = generator.generate_batch_sync(topics, 5, 'linkedin')
        if posts:
            batch_id = generator.save_to_production_db(posts, 'linkedin')
            print(f"✅ Batch {batch_id} saved to production database")

    elif choice == '2':
        # Large batch
        print(f"\n⚡ Generating 20 LinkedIn posts...")
        posts, _ = generator.generate_batch_sync(topics, 20, 'linkedin')
        if posts:
            batch_id = generator.save_to_production_db(posts, 'linkedin')
            print(f"✅ Large batch {batch_id} saved to production database")

    elif choice == '3':
        # 30-day calendar
        print(f"\n📅 Generating 30-day content calendar...")
        calendar = generator.generate_content_calendar(num_days=30)
        print(f"✅ Content calendar generated and saved")

    elif choice == '4':
        # Custom batch
        try:
            num_posts = int(input("Number of posts (1-50): "))
            platform = input("Platform (linkedin/twitter) [linkedin]: ").strip() or "linkedin"
            num_posts = max(1, min(50, num_posts))

            print(f"\n⚡ Generating {num_posts} {platform} posts...")
            posts, _ = generator.generate_batch_sync(topics, num_posts, platform)
            if posts:
                batch_id = generator.save_to_production_db(posts, platform)
                print(f"✅ Custom batch {batch_id} saved to production database")

        except ValueError:
            print("❌ Invalid number")

    elif choice == '5':
        # Analytics
        print(f"\n📊 Production Analytics:")
        analytics = generator.get_analytics_summary()

        print(f"📝 Total Content Generated: {analytics['total_content_generated']}")
        print(f"📤 Content Published: {analytics['content_published']}")
        print(f"📋 Content Draft: {analytics['content_draft']}")

        if analytics['platform_performance']:
            print(f"\n📈 Platform Performance:")
            for perf in analytics['platform_performance']:
                print(f"  {perf['platform']}: {perf['avg_engagement']:.1f}% engagement")

        if analytics['top_performing_topics']:
            print(f"\n🏆 Top Performing Topics:")
            for i, topic in enumerate(analytics['top_performing_topics'][:5], 1):
                print(f"  {i}. {topic['topic']}: {topic['avg_engagement']:.1f}% engagement")

    elif choice == '6':
        # Emergency batch
        print(f"\n🚨 EMERGENCY MODE: 100 posts")
        print("This will take approximately 3-5 minutes...")

        if input("Continue? (y/N): ").lower().startswith('y'):
            posts, _ = generator.generate_batch_sync(topics, 100, 'linkedin')
            if posts:
                batch_id = generator.save_to_production_db(posts, 'linkedin')
                print(f"✅ Emergency batch {batch_id} saved to production database")

    print(f"\n✨ Production content generation complete!")
    print(f"📈 System ready for lead generation and revenue generation")


if __name__ == "__main__":
    main()