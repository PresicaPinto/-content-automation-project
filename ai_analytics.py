"""
AI-Powered Content Analytics Engine
Analyzes real content data to generate actionable insights
"""

import sqlite3
import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import statistics
import os

class AIContentAnalyzer:
    def __init__(self):
        self.db_path = 'data/metrics.db'
        # Ensure database directory exists
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def analyze_content_performance(self):
        """Analyze content performance trends"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get content from last 30 days
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

                cursor.execute('''
                    SELECT platform, topic, content, generated_at, hashtags, style
                    FROM generated_content
                    WHERE generated_at >= ?
                    ORDER BY generated_at DESC
                ''', (thirty_days_ago,))

                content_data = cursor.fetchall()

                if not content_data:
                    return self._generate_default_insights()

                return self._analyze_content_patterns(content_data)

        except Exception as e:
            print(f"Error analyzing content: {e}")
            return self._generate_default_insights()

    def _analyze_content_patterns(self, content_data):
        """Analyze patterns in content data"""
        insights = []

        # Platform Performance Analysis
        platform_stats = defaultdict(list)
        topic_performance = defaultdict(list)
        content_lengths = []
        hashtag_analysis = []

        for row in content_data:
            platform, topic, content, generated_at, hashtags, style = row

            # Platform analysis
            platform_stats[platform].append({
                'topic': topic,
                'content_length': len(content),
                'hashtags': hashtags,
                'date': generated_at
            })

            # Topic analysis
            if topic:
                topic_performance[topic].append(len(content))
                content_lengths.append(len(content))

            # Hashtag analysis
            if hashtags:
                tags = [tag.strip() for tag in hashtags.split() if tag.startswith('#')]
                hashtag_analysis.extend(tags)

        # Generate insights from analysis
        insights.extend(self._generate_platform_insights(platform_stats))
        insights.extend(self._generate_topic_insights(topic_performance))
        insights.extend(self._generate_content_length_insights(content_lengths))
        insights.extend(self._generate_hashtag_insights(hashtag_analysis))
        insights.extend(self._generate_timing_insights(content_data))

        return insights[:6]  # Return top 6 insights

    def _generate_platform_insights(self, platform_stats):
        """Generate platform-specific insights"""
        insights = []

        # Most active platform
        if platform_stats:
            most_active = max(platform_stats.keys(), key=lambda k: len(platform_stats[k]))
            insights.append({
                'type': 'platform_performance',
                'title': f'{most_active.title()} Dominance',
                'description': f'Your {most_active} content is performing best with {len(platform_stats[most_active])} posts this month.',
                'recommendation': f'Focus more resources on {most_active} for maximum engagement.',
                'icon': 'fas fa-chart-line',
                'color': 'success'
            })

            # Platform with highest engagement potential
            avg_lengths = {platform: statistics.mean([post['content_length'] for post in posts])
                          for platform, posts in platform_stats.items()}

            if len(avg_lengths) > 1:
                best_platform = max(avg_lengths.keys(), key=lambda k: avg_lengths[k])
                insights.append({
                    'type': 'content_optimization',
                    'title': 'Content Length Strategy',
                    'description': f'{best_platform.title()} posts perform best with {int(avg_lengths[best_platform])} characters on average.',
                    'recommendation': 'Optimize your content length based on platform preferences.',
                    'icon': 'fas fa-ruler-horizontal',
                    'color': 'info'
                })

        return insights

    def _generate_topic_insights(self, topic_performance):
        """Generate topic-based insights"""
        insights = []

        if topic_performance:
            # Most successful topic
            topic_averages = {topic: statistics.mean(lengths) for topic, lengths in topic_performance.items() if lengths}

            if topic_averages:
                best_topic = max(topic_averages.keys(), key=lambda k: topic_averages[k])
                insights.append({
                    'type': 'topic_success',
                    'title': 'Top Performing Topic',
                    'description': f'"{best_topic}" generates your most engaging content with detailed posts.',
                    'recommendation': f'Create more content around {best_topic} to boost engagement.',
                    'icon': 'fas fa-fire',
                    'color': 'warning'
                })

                # Topic diversity analysis
                if len(topic_averages) > 3:
                    insights.append({
                        'type': 'content_diversity',
                        'title': 'Content Variety',
                        'description': f'You\'re covering {len(topic_averages)} different topics - great for audience engagement!',
                        'recommendation': 'Maintain this diverse content strategy to reach wider audiences.',
                        'icon': 'fas fa-palette',
                        'color': 'primary'
                    })

        return insights

    def _generate_content_length_insights(self, content_lengths):
        """Generate content length insights"""
        insights = []

        if content_lengths:
            avg_length = statistics.mean(content_lengths)

            if avg_length > 1000:
                insights.append({
                    'type': 'content_strategy',
                    'title': 'Detailed Content Strategy',
                    'description': f'Your posts average {int(avg_length)} characters - audiences love comprehensive content!',
                    'recommendation': 'Continue providing value-packed content that addresses audience pain points.',
                    'icon': 'fas fa-align-left',
                    'color': 'success'
                })
            elif avg_length < 500:
                insights.append({
                    'type': 'content_improvement',
                    'title': 'Content Expansion Opportunity',
                    'description': f'Your posts average {int(avg_length)} characters - consider adding more depth.',
                    'recommendation': 'Expand your content with examples, data, and actionable insights.',
                    'icon': 'fas fa-expand-alt',
                    'color': 'info'
                })

        return insights

    def _generate_hashtag_insights(self, hashtag_analysis):
        """Generate hashtag-related insights"""
        insights = []

        if hashtag_analysis:
            hashtag_counts = Counter(hashtag_analysis)
            top_hashtags = hashtag_counts.most_common(5)

            if top_hashtags:
                top_tag, count = top_hashtags[0]
                insights.append({
                    'type': 'hashtag_strategy',
                    'title': 'Hashtag Performance',
                    'description': f'#{top_tag} is your most successful hashtag, used in {count} posts.',
                    'recommendation': 'Build hashtag clusters around your top performers for better reach.',
                    'icon': 'fas fa-hashtag',
                    'color': 'primary'
                })

                if len(hashtag_counts) > 10:
                    insights.append({
                        'type': 'hashtag_diversity',
                        'title': 'Hashtag Strategy',
                        'description': f'You\'re using {len(hashtag_counts)} different hashtags - excellent for discoverability!',
                        'recommendation': 'Continue diversifying hashtags while maintaining relevance.',
                        'icon': 'fas fa-tags',
                        'color': 'success'
                    })

        return insights

    def _generate_timing_insights(self, content_data):
        """Generate timing-related insights"""
        insights = []

        if content_data:
            # Analyze posting patterns
            dates = [datetime.fromisoformat(row[3].replace('Z', '+00:00')) for row in content_data]

            if len(dates) > 1:
                # Calculate posting frequency
                date_range = (max(dates) - min(dates)).days
                if date_range > 0:
                    frequency = len(dates) / date_range

                    if frequency > 1:
                        insights.append({
                            'type': 'posting_frequency',
                            'title': 'Consistent Posting',
                            'description': f'You\'re posting {frequency:.1f} times per day - great for algorithm visibility!',
                            'recommendation': 'Maintain this consistent posting schedule for optimal reach.',
                            'icon': 'fas fa-clock',
                            'color': 'success'
                        })
                    elif frequency < 0.3:
                        insights.append({
                            'type': 'posting_frequency',
                            'title': 'Posting Opportunity',
                            'description': f'You\'re posting {frequency*7:.1f} times per week - consider increasing frequency.',
                            'recommendation': 'Aim for 3-5 posts per week to maintain audience engagement.',
                            'icon': 'fas fa-calendar-plus',
                            'color': 'warning'
                        })

        return insights

    def _generate_default_insights(self):
        """Generate default insights when no data is available"""
        return [
            {
                'type': 'getting_started',
                'title': 'Start Your Content Journey',
                'description': 'Begin generating content to unlock AI-powered insights tailored to your strategy.',
                'recommendation': 'Create your first few posts and watch as the AI learns your patterns.',
                'icon': 'fas fa-rocket',
                'color': 'info'
            },
            {
                'type': 'content_strategy',
                'title': 'Content Strategy Builder',
                'description': 'Your content performance data will help shape optimal posting strategies.',
                'recommendation': 'Focus on educational content first - it typically generates 2x more engagement.',
                'icon': 'fas fa-lightbulb',
                'color': 'warning'
            },
            {
                'type': 'platform_optimization',
                'title': 'Platform Excellence',
                'description': 'Different platforms require different approaches for maximum impact.',
                'recommendation': 'LinkedIn thrives on professional insights, Instagram on visual storytelling.',
                'icon': 'fas fa-globe',
                'color': 'primary'
            }
        ]

    def predict_best_posting_time(self):
        """Predict optimal posting times based on historical data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT platform, generated_at
                    FROM generated_content
                    WHERE generated_at >= date('now', '-30 days')
                    ORDER BY generated_at DESC
                ''')

                posts = cursor.fetchall()

                if not posts:
                    return "9:00 AM - 11:00 AM"

                # Analyze posting patterns by hour
                hour_counts = defaultdict(int)
                for platform, timestamp in posts:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        hour_counts[dt.hour] += 1
                    except:
                        continue

                if hour_counts:
                    best_hour = max(hour_counts.keys(), key=lambda k: hour_counts[k])
                    return f"{best_hour}:00 - {best_hour+1}:00"

        except Exception as e:
            print(f"Error predicting posting time: {e}")

        return "9:00 AM - 11:00 AM"

    def get_content_recommendations(self):
        """Get AI-powered content recommendations"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT topic, platform, style
                    FROM generated_content
                    WHERE generated_at >= date('now', '-30 days')
                    LIMIT 10
                ''')

                recent_content = cursor.fetchall()

                if not recent_content:
                    return [
                        "Start with educational content about your industry",
                        "Share personal experiences and case studies",
                        "Use storytelling to make complex topics relatable"
                    ]

                # Analyze successful patterns
                topics = [row[0] for row in recent_content if row[0]]
                platforms = [row[1] for row in recent_content]
                styles = [row[2] for row in recent_content if row[2]]

                recommendations = []

                # Topic-based recommendations
                if topics:
                    most_common_topic = Counter(topics).most_common(1)[0][0]
                    recommendations.append(f"Expand on '{most_common_topic}' with deeper insights and examples")

                # Platform-specific recommendations
                if 'linkedin' in platforms:
                    recommendations.append("Create more professional insights with data-backed claims")

                if 'instagram' in platforms:
                    recommendations.append("Add more visual elements and behind-the-scenes content")

                # Style recommendations
                if 'educational' in styles:
                    recommendations.append("Include practical takeaways and actionable advice")

                return recommendations[:3]

        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return [
                "Focus on providing genuine value to your audience",
                "Share authentic experiences and lessons learned",
                "Use data and examples to support your claims"
            ]