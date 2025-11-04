import requests
import json
from datetime import datetime, timedelta
import os

class SocialMediaScheduler:
    def __init__(self, buffer_access_token):
        if not buffer_access_token:
            raise ValueError("Buffer Access Token is required for SocialMediaScheduler.")
        self.buffer_token = buffer_access_token
        self.base_url = "https://api.bufferapp.com/1"

    def get_profiles(self):
        """Get all connected social media profiles"""
        url = f"{self.base_url}/profiles.json"
        params = {'access_token': self.buffer_token}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting Buffer profiles: {e}")
            return None

    def schedule_post(self, profile_id, text, scheduled_at, media=None):
        """
        Schedule a post to Buffer

        Args:
            profile_id (str): Buffer profile ID
            text (str): Post content
            scheduled_at (datetime): When to publish
            media (dict): Optional media attachment

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/updates/create.json"

        data = {
            'access_token': self.buffer_token,
            'profile_ids[]': [profile_id],
            'text': text,
            'scheduled_at': int(scheduled_at.timestamp()),
            'shorten': True  # Auto-shorten links
        }

        if media:
            data['media'] = media

        try:
            response = requests.post(url, data=data)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error scheduling post to Buffer: {e}")
            return {'success': False, 'error': str(e)}

    def schedule_content_calendar(self, content_calendar, linkedin_profile_id):
        """Schedule entire content calendar"""
        results = []

        print(f"\n--- Scheduling {len(content_calendar)} LinkedIn posts ---")
        for item in content_calendar:
            # Parse scheduled date
            publish_date = datetime.strptime(item['publish_date'], '%Y-%m-%d')
            # Set publish time (e.g., 9 AM)
            publish_date = publish_date.replace(hour=9, minute=0)

            print(f"Scheduling LinkedIn post for {item['topic']} on {publish_date.strftime('%Y-%m-%d %H:%M')}")
            result = self.schedule_post(
                profile_id=linkedin_profile_id,
                text=item['content'],
                scheduled_at=publish_date
            )

            results.append({
                'post_number': item['post_number'],
                'topic': item['topic'],
                'scheduled': result.get('success', False),
                'buffer_id': result.get('id', None),
                'error': result.get('error')
            })

        return results

    def schedule_twitter_threads(self, twitter_calendar, twitter_profile_id):
        """Schedule Twitter threads (multiple tweets)"""
        results = []

        print(f"\n--- Scheduling {len(twitter_calendar)} Twitter threads ---")
        for item in twitter_calendar:
            publish_date = datetime.strptime(item['publish_date'], '%Y-%m-%d')
            publish_date = publish_date.replace(hour=14, minute=0)  # 2 PM

            print(f"Scheduling Twitter thread for {item['topic']} starting {publish_date.strftime('%Y-%m-%d %H:%M')}")
            thread_results = []
            # Schedule each tweet in thread with 2-min gaps
            for i, tweet in enumerate(item['tweets']):
                tweet_time = publish_date + timedelta(minutes=i*2)

                print(f"  - Scheduling tweet {i+1}/{len(item['tweets'])} for {tweet_time.strftime('%H:%M')}")
                result = self.schedule_post(
                    profile_id=twitter_profile_id,
                    text=tweet,
                    scheduled_at=tweet_time
                )
                thread_results.append({
                    'tweet_number': i + 1,
                    'scheduled': result.get('success', False),
                    'buffer_id': result.get('id', None),
                    'error': result.get('error')
                })

            results.append({
                'post_number': item['post_number'],
                'topic': item['topic'],
                'tweets_scheduled': len(item['tweets']),
                'thread_schedule_results': thread_results
            })

        return results

if __name__ == "__main__":
    # Example Usage (requires BUFFER_ACCESS_TOKEN in .env)
    # and actual profile IDs
    load_dotenv()
    BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")

    if not BUFFER_ACCESS_TOKEN:
        print("Please set BUFFER_ACCESS_TOKEN in your .env file for example usage.")
    else:
        scheduler = SocialMediaScheduler(BUFFER_ACCESS_TOKEN)
        profiles = scheduler.get_profiles()
        if profiles:
            print("\nConnected Buffer Profiles:")
            for p in profiles:
                print(f"- {p['service'].capitalize()} ({p['service_display_name']}): ID={p['id']}")

            # Dummy data for scheduling example
            dummy_linkedin_calendar = [
                {
                    'post_number': 1,
                    'topic': 'Test LinkedIn Post',
                    'content': 'This is a test LinkedIn post scheduled via Buffer API.',
                    'publish_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'platform': 'linkedin',
                    'status': 'draft'
                }
            ]
            dummy_twitter_calendar = [
                {
                    'post_number': 1,
                    'topic': 'Test Twitter Thread',
                    'tweets': [
                        '1/2 This is tweet 1 of a test thread.',
                        '2/2 This is tweet 2 of a test thread. #Test #BufferAPI'
                    ],
                    'publish_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'platform': 'twitter',
                    'status': 'draft'
                }
            ]

            # Replace with actual profile IDs from get_profiles() output
            # linkedin_profile_id = "YOUR_LINKEDIN_PROFILE_ID"
            # twitter_profile_id = "YOUR_TWITTER_PROFILE_ID"

            # print("\nAttempting to schedule dummy LinkedIn post...")
            # linkedin_results = scheduler.schedule_content_calendar(dummy_linkedin_calendar, linkedin_profile_id)
            # print(json.dumps(linkedin_results, indent=2))

            # print("\nAttempting to schedule dummy Twitter thread...")
            # twitter_results = scheduler.schedule_twitter_threads(dummy_twitter_calendar, twitter_profile_id)
            # print(json.dumps(twitter_results, indent=2))
        else:
            print("Could not retrieve Buffer profiles. Check your access token.")
