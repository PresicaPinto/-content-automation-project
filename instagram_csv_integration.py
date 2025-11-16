#!/usr/bin/env python3
"""
Instagram CSV Integration - Manual Data Entry System
Import and manage Instagram metrics via CSV files
"""

import csv
import os
import json
from datetime import datetime
from pathlib import Path

class InstagramCSVIntegration:
    """Handle Instagram metrics through CSV files"""

    def __init__(self):
        self.csv_path = "data/instagram_metrics.csv"
        self.sample_csv_path = "data/sample_instagram_metrics.csv"
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.create_sample_csv()

    def create_sample_csv(self):
        """Create a sample CSV template"""
        if not os.path.exists(self.sample_csv_path):
            sample_data = [
                ["Date", "Post_URL", "Image_URL", "Caption", "Likes", "Comments", "Shares", "Saves", "Reach", "Impressions"],
                ["2024-11-10", "https://instagram.com/p/ABC123", "https://example.com/image1.jpg", "Check out our latest AI automation solution!", 45, 12, 5, 8, 1200, 2500],
                ["2024-11-09", "https://instagram.com/p/XYZ789", "https://example.com/image2.jpg", "Behind the scenes of our development process", 32, 8, 3, 6, 980, 1800],
                ["2024-11-08", "https://instagram.com/p/DEF456", "https://example.com/image3.jpg", "Machine learning breakthrough achieved!", 67, 15, 8, 12, 1500, 3200]
            ]

            with open(self.sample_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)

            print(f"✅ Sample CSV created at: {self.sample_csv_path}")

    def import_csv(self, csv_file_path=None):
        """Import Instagram metrics from CSV file"""
        if csv_file_path is None:
            csv_file_path = self.csv_path

        if not os.path.exists(csv_file_path):
            return {"success": False, "error": f"CSV file not found: {csv_file_path}"}

        metrics_data = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Calculate engagement rate
                    total_engagement = int(row.get('Likes', 0)) + int(row.get('Comments', 0)) + int(row.get('Shares', 0))
                    reach = int(row.get('Reach', 1))
                    engagement_rate = (total_engagement / reach) * 100 if reach > 0 else 0

                    metrics_data.append({
                        'date': row.get('Date', ''),
                        'platform': 'instagram',
                        'post_url': row.get('Post_URL', ''),
                        'image_url': row.get('Image_URL', ''),
                        'caption': row.get('Caption', '')[:200],  # Truncate for display
                        'likes': int(row.get('Likes', 0)),
                        'comments': int(row.get('Comments', 0)),
                        'shares': int(row.get('Shares', 0)),
                        'saves': int(row.get('Saves', 0)),
                        'reach': int(row.get('Reach', 0)),
                        'impressions': int(row.get('Impressions', 0)),
                        'engagement_rate': round(engagement_rate, 2),
                        'total_engagement': total_engagement
                    })

            return {
                "success": True,
                "data": metrics_data,
                "count": len(metrics_data)
            }

        except Exception as e:
            return {"success": False, "error": f"Error reading CSV: {str(e)}"}

    def export_template(self):
        """Create a fresh CSV template for manual entry"""
        template_path = "data/instagram_metrics_template.csv"

        headers = [
            "Date", "Post_URL", "Image_URL", "Caption",
            "Likes", "Comments", "Shares", "Saves", "Reach", "Impressions"
        ]

        with open(template_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            # Add sample row for guidance
            writer.writerow([
                "2024-11-10",
                "https://instagram.com/p/YOUR_POST_ID",
                "https://example.com/your-image.jpg",
                "Your post caption here...",
                0, 0, 0, 0, 0, 0
            ])

        print(f"✅ Template created at: {template_path}")
        return template_path

    def save_metrics(self, metrics_data):
        """Save metrics data to CSV file"""
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                "Date", "Platform", "Post_URL", "Image_URL", "Caption",
                "Likes", "Comments", "Shares", "Saves", "Reach",
                "Impressions", "Engagement_Rate", "Total_Engagement"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for data in metrics_data:
                writer.writerow({
                    "Date": data.get('date', ''),
                    "Platform": data.get('platform', 'instagram'),
                    "Post_URL": data.get('post_url', ''),
                    "Image_URL": data.get('image_url', ''),
                    "Caption": data.get('caption', ''),
                    "Likes": data.get('likes', 0),
                    "Comments": data.get('comments', 0),
                    "Shares": data.get('shares', 0),
                    "Saves": data.get('saves', 0),
                    "Reach": data.get('reach', 0),
                    "Impressions": data.get('impressions', 0),
                    "Engagement_Rate": data.get('engagement_rate', 0),
                    "Total_Engagement": data.get('total_engagement', 0)
                })

        return self.csv_path

    def get_summary_stats(self):
        """Get summary statistics from imported data"""
        result = self.import_csv()
        if not result['success']:
            return {"success": False, "error": "No data available"}

        data = result['data']
        if not data:
            return {"success": False, "error": "Empty dataset"}

        total_posts = len(data)
        total_likes = sum(item['likes'] for item in data)
        total_comments = sum(item['comments'] for item in data)
        total_shares = sum(item['shares'] for item in data)
        total_reach = sum(item['reach'] for item in data)
        total_engagement = sum(item['total_engagement'] for item in data)

        avg_engagement_rate = sum(item['engagement_rate'] for item in data) / total_posts

        # Best performing post
        best_post = max(data, key=lambda x: x['engagement_rate'])

        return {
            "success": True,
            "stats": {
                "total_posts": total_posts,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_reach": total_reach,
                "total_engagement": total_engagement,
                "avg_engagement_rate": round(avg_engagement_rate, 2),
                "best_post": best_post
            }
        }

# Usage Example
if __name__ == "__main__":
    instagram = InstagramCSVIntegration()

    # Create template
    template_path = instagram.export_template()
    print(f"Template created: {template_path}")

    # Test import with sample data
    result = instagram.import_csv(instagram.sample_csv_path)
    print(f"Import result: {result}")

    # Get stats
    stats = instagram.get_summary_stats()
    print(f"Summary stats: {stats}")