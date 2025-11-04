import os
import json
import logging
from datetime import datetime, timedelta
from core.ai_client import generate_content
from prompts.platform_prompts import get_prompt
from core import config

logger = logging.getLogger(__name__)

class TwitterThreadGenerator:
    def __init__(self):
        self.output_dir = config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_twitter_calendar(self, linkedin_calendar: list):
        if not linkedin_calendar:
            logger.warning("Error: LinkedIn content calendar is empty or not provided. Please generate LinkedIn posts first.")
            return []
        twitter_content_calendar = []
        base_date = datetime.now()

        logger.info(f"Starting Twitter thread generation from {len(linkedin_calendar)} LinkedIn posts.")

        for i, linkedin_post in enumerate(linkedin_calendar):
            topic = linkedin_post['topic']
            prompt_type = "thread_starter"

            # Generate the first tweet of the thread
            formatted_prompt = get_prompt("twitter", prompt_type, topic)
            first_tweet = generate_content(formatted_prompt)

            # Generate the rest of the thread
            thread_tweets = [first_tweet]
            for _ in range(2): # Generate 2 more tweets for the thread
                prompt = f"Continue the Twitter thread on the topic: {topic}. The previous tweet was: {thread_tweets[-1]}"
                next_tweet = generate_content(prompt)
                thread_tweets.append(next_tweet)

            publish_date = base_date + timedelta(days=i)

            twitter_content_calendar.append({
                'post_number': i + 1,
                'topic': topic,
                'platform': "twitter",
                'prompt_type': "thread",
                'content': thread_tweets,
                'publish_date': publish_date.strftime('%Y-%m-%d'),
                'status': 'draft'
            })
            logger.info(f"Generated thread {i+1}/{len(linkedin_calendar)} for topic: {topic[:30]}...")

        twitter_output_file_path = os.path.join(self.output_dir, config.TWITTER_OUTPUT_FILE)

        with open(twitter_output_file_path, 'w') as f:
            json.dump(twitter_content_calendar, f, indent=2)

        logger.info(f"Twitter thread generation complete. Twitter calendar saved to {twitter_output_file_path}")
        logger.info(f"Generated {len(twitter_content_calendar)} Twitter threads.")

        return twitter_content_calendar

if __name__ == "__main__":
    # Example usage
    # First, generate LinkedIn posts to have a calendar to work with
    from linkedin_generator import LinkedInGenerator
    linkedin_generator = LinkedInGenerator()
    linkedin_calendar = linkedin_generator.generate_linkedin_posts(num_posts=3)

    # Now, generate Twitter threads from the LinkedIn calendar
    twitter_generator = TwitterThreadGenerator()
    twitter_calendar = twitter_generator.generate_twitter_calendar(linkedin_calendar)
    # print(json.dumps(twitter_calendar, indent=2))
