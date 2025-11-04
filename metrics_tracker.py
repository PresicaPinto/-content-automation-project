import csv
from datetime import datetime
import os

class MetricsTracker:
    def __init__(self, csv_file='outputs/metrics.csv'):
        self.csv_file = csv_file
        self._init_csv()

    def _init_csv(self):
        """Initialize CSV with headers"""
        # Ensure the outputs directory exists
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        try:
            with open(self.csv_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Platform', 'Post_Number', 'Topic',
                    'Views', 'Likes', 'Comments', 'Shares', 'Engagement_Rate'
                ])
        except FileExistsError:
            pass # File already exists, no need to re-initialize

    def log_metrics(self, platform, post_number, topic, views, likes, comments, shares):
        """Log metrics for a post"""
        # Ensure views is not zero to avoid division by zero
        engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0.0

        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d'),
                platform,
                post_number,
                topic,
                views,
                likes,
                comments,
                shares,
                f"{engagement_rate:.2f}%"
            ])
        print(f"Logged metrics for {platform} post {post_number}.")

    def get_summary(self):
        """Get summary statistics"""
        # TODO: Implement analytics - this is a placeholder for future development
        print("Summary statistics not yet implemented.")
        pass

if __name__ == "__main__":
    # Example usage
    tracker = MetricsTracker()

    print("\n--- Logging Example Metrics ---")
    # Example: LinkedIn post got 500 views, 20 likes, 5 comments, 2 shares
    tracker.log_metrics(
        platform='linkedin',
        post_number=1,
        topic='AI Health Coach',
        views=500,
        likes=20,
        comments=5,
        shares=2
    )

    # Example: Twitter thread got 1200 views, 50 likes, 10 comments, 15 shares
    tracker.log_metrics(
        platform='twitter',
        post_number=1,
        topic='AI Health Coach',
        views=1200,
        likes=50,
        comments=10,
        shares=15
    )

    print("\nMetrics logged to outputs/metrics.csv")
