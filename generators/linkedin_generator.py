import os
import json
import logging
from datetime import datetime, timedelta
from core.ai_client import generate_content
from prompts.platform_prompts import get_prompt
from core import config

logger = logging.getLogger(__name__)

class LinkedInGenerator:
    def __init__(self):
        self.topics_file = config.TOPICS_FILE
        self.output_dir = config.settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_linkedin_posts(self, num_posts: int = None):
        try:
            with open(self.topics_file, 'r') as f:
                topics_data = json.load(f)
        except FileNotFoundError:
            logger.error(f"Error: {self.topics_file} not found. Please create it with content ideas.")
            return []
        except json.JSONDecodeError:
            logger.error(f"Error: Invalid JSON in {self.topics_file}. Please check the file format.")
            return []

        if not topics_data:
            logger.warning("Error: No topics found in {self.topics_file}. Please add some topics to generate content.")
            return []

        if num_posts is None:
            num_posts = len(topics_data)
        else:
            topics_data = topics_data[:num_posts]  # Limit to num_posts if specified

        linkedin_content_calendar = []
        base_date = datetime.now()

        logger.info(f"Starting batch content generation for {len(topics_data)} LinkedIn posts.")

        for i, item in enumerate(topics_data):
            topic = item['topic']
            prompt_type = "professional_post" # Using professional_post for all LinkedIn for now

            formatted_prompt = get_prompt("linkedin", prompt_type, topic)
            generated_text = generate_content(formatted_prompt)

            publish_date = base_date + timedelta(days=i)

            linkedin_content_calendar.append({
                'post_number': i + 1,
                'topic': topic,
                'platform': "linkedin",
                'prompt_type': prompt_type,
                'content': generated_text,
                'publish_date': publish_date.strftime('%Y-%m-%d'),
                'status': 'draft'
            })
            logger.info(f"Generated post {i+1}/{len(topics_data)} for topic: {topic[:30]}...")

        linkedin_output_file_path = os.path.join(self.output_dir, config.LINKEDIN_OUTPUT_FILE)

        with open(linkedin_output_file_path, 'w') as f:
            json.dump(linkedin_content_calendar, f, indent=2)

        logger.info(f"LinkedIn batch content generation complete. Content calendar saved to {linkedin_output_file_path}")
        logger.info(f"Generated {len(linkedin_content_calendar)} LinkedIn posts.")

        return linkedin_content_calendar

if __name__ == "__main__":
    # Example usage
    generator = LinkedInGenerator()
    calendar = generator.generate_linkedin_posts(num_posts=3) # Generate 3 posts for example
    # print(json.dumps(calendar, indent=2))
