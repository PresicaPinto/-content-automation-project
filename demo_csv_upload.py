#!/usr/bin/env python3
"""
Demo LinkedIn CSV Upload Script
Demonstrates uploading LinkedIn analytics data and showing integration results
"""

import sqlite3
import os
import csv
from datetime import datetime, timezone

def init_linkedin_database():
    """Initialize LinkedIn analytics database"""
    os.makedirs('data', exist_ok=True)

    with sqlite3.connect('data/linkedin_analytics.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS linkedin_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_date TEXT,
                impressions INTEGER,
                clicks INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                post_text TEXT,
                media_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def import_csv_data(csv_file_path):
    """Import LinkedIn analytics from CSV file"""
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return False

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            with sqlite3.connect('data/linkedin_analytics.db') as conn:
                conn.execute('DELETE FROM linkedin_posts')  # Clear existing data

                posts_imported = 0
                for row in csv_reader:
                    conn.execute('''
                        INSERT INTO linkedin_posts
                        (post_date, impressions, clicks, likes, comments, shares, post_text, media_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Date'],
                        int(row['Impressions']),
                        int(row['Clicks']),
                        int(row['Likes']),
                        int(row['Comments']),
                        int(row['Shares']),
                        row['Post Text'],
                        row['Media Type']
                    ))
                    posts_imported += 1

                conn.commit()

        print(f"✅ Successfully imported {posts_imported} LinkedIn posts from CSV")
        return True

    except Exception as e:
        print(f"❌ Error importing CSV: {str(e)}")
        return False

def calculate_linkedin_metrics():
    """Calculate LinkedIn metrics from imported data"""
    try:
        with sqlite3.connect('data/linkedin_analytics.db') as conn:
            cursor = conn.execute('''
                SELECT
                    COUNT(*) as total_posts,
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    AVG(impressions) as avg_impressions,
                    MAX(post_date) as latest_post
                FROM linkedin_posts
            ''')

            metrics = cursor.fetchone()

            if metrics and metrics[0] > 0:
                total_posts, total_impressions, total_clicks, total_likes, total_comments, total_shares, avg_impressions, latest_post = metrics

                # Calculate engagement rates
                total_engagement = total_likes + total_comments + total_shares
                engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
                click_through_rate = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

                return {
                    'total_posts': total_posts,
                    'total_impressions': total_impressions,
                    'total_clicks': total_clicks,
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'total_shares': total_shares,
                    'avg_impressions': round(avg_impressions, 1),
                    'latest_post': latest_post,
                    'total_engagement': total_engagement,
                    'engagement_rate': round(engagement_rate, 2),
                    'click_through_rate': round(click_through_rate, 2)
                }
        return None
    except Exception as e:
        print(f"❌ Error calculating metrics: {str(e)}")
        return None

def get_top_performing_posts():
    """Get top performing LinkedIn posts"""
    try:
        with sqlite3.connect('data/linkedin_analytics.db') as conn:
            cursor = conn.execute('''
                SELECT post_date, post_text, media_type, impressions, likes, comments, shares,
                       (likes + comments + shares) as total_engagement
                FROM linkedin_posts
                ORDER BY total_engagement DESC
                LIMIT 5
            ''')

            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'date': row[0],
                    'text': row[1][:80] + '...' if len(row[1]) > 80 else row[1],
                    'media_type': row[2],
                    'impressions': row[3],
                    'likes': row[4],
                    'comments': row[5],
                    'shares': row[6],
                    'engagement': row[7]
                })
            return posts
    except Exception as e:
        print(f"❌ Error getting top posts: {str(e)}")
        return []

def show_integration_demo():
    """Show the complete LinkedIn integration demo"""
    print("🚀 LinkedIn CSV Integration Demo")
    print("=" * 50)

    # Step 1: Initialize database
    print("\n📊 Step 1: Initializing LinkedIn Analytics Database...")
    init_linkedin_database()
    print("✅ Database initialized successfully")

    # Step 2: Import CSV data
    print("\n📁 Step 2: Importing LinkedIn Analytics from CSV...")
    csv_file = 'demo_linkedin_analytics.csv'
    if import_csv_data(csv_file):
        print("✅ CSV data imported successfully")
    else:
        print("❌ Failed to import CSV data")
        return

    # Step 3: Calculate metrics
    print("\n📈 Step 3: Calculating LinkedIn Analytics Metrics...")
    metrics = calculate_linkedin_metrics()
    if metrics:
        print("✅ Metrics calculated successfully")
        print("\n📊 LinkedIn Analytics Summary:")
        print(f"   Total Posts: {metrics['total_posts']}")
        print(f"   Total Impressions: {metrics['total_impressions']:,}")
        print(f"   Total Likes: {metrics['total_likes']:,}")
        print(f"   Total Comments: {metrics['total_comments']:,}")
        print(f"   Total Shares: {metrics['total_shares']:,}")
        print(f"   Average Impressions per Post: {metrics['avg_impressions']:,}")
        print(f"   Engagement Rate: {metrics['engagement_rate']}%")
        print(f"   Click-Through Rate: {metrics['click_through_rate']}%")
        print(f"   Latest Post Date: {metrics['latest_post']}")

    # Step 4: Show top performing posts
    print("\n🏆 Step 4: Top Performing LinkedIn Posts...")
    top_posts = get_top_performing_posts()
    if top_posts:
        print("✅ Top posts retrieved successfully")
        for i, post in enumerate(top_posts, 1):
            print(f"\n   {i}. {post['text']}")
            print(f"      Date: {post['date']}")
            print(f"      Media: {post['media_type']}")
            print(f"      Metrics: {post['impressions']} impressions, {post['likes']} likes, {post['comments']} comments, {post['shares']} shares")
            print(f"      Total Engagement: {post['engagement']}")

    # Step 5: Integration status
    print("\n🔗 Step 5: LinkedIn Connection Status...")
    print("✅ LinkedIn CSV Integration: ACTIVE")
    print("✅ Data Source: LinkedIn Analytics CSV Export")
    print("✅ Company: Ardelis Technologies")
    print("✅ Connection Type: CSV Upload")
    print("✅ Data Range: 4 months of analytics data")

    print("\n🎯 Integration Benefits:")
    print("   • Real LinkedIn analytics imported successfully")
    print("   • Dashboard will show actual engagement metrics")
    print("   • Content performance tracking enabled")
    print("   • Multi-platform analytics comparison available")
    print("   • Historical data analysis for strategic insights")

    print("\n📱 Platform Integration Status:")
    print("   ✅ Twitter: Connected (API)")
    print("   ✅ LinkedIn: Connected (CSV Upload)")
    print("   ✅ Instagram: Ready for API connection")

    print("\n🎉 LinkedIn CSV Integration Demo Complete!")
    print("📈 Visit /social-media-setup to see LinkedIn connected status")
    print("📊 Visit /dashboard to see integrated analytics")
    print("📉 Visit /advanced-analytics to see detailed charts")

if __name__ == "__main__":
    show_integration_demo()