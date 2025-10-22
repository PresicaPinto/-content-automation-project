import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zai import ZaiClient # Correct import for zai-sdk

load_dotenv() # Load environment variables from .env file

ZAI_API_KEY = os.getenv("ZAI_API_KEY")

if not ZAI_API_KEY:
    raise ValueError("ZAI_API_KEY not found in environment variables. Please set it in a .env file.")

client = ZaiClient(api_key=ZAI_API_KEY)

class TwitterThreadGenerator:
    def __init__(self):
        self.client = client # Use the already initialized ZaiClient

    def linkedin_to_twitter(self, linkedin_post):
        """
        Convert LinkedIn post to Twitter thread

        Args:
            linkedin_post (str): Original LinkedIn post

        Returns:
            list: List of tweets (280 char max each)
        """

        prompt = f"""Convert this LinkedIn post into a Twitter thread.

LinkedIn Post:
{linkedin_post}

Requirements:
- 5-10 tweets total
- Each tweet max 280 characters
- Tweet 1: Compelling hook
- Tweets 2-8: One insight per tweet
- Last tweet: CTA or key takeaway
- More casual/punchy than LinkedIn
- Can use light formatting (→, •, etc.)

Return as JSON array: ["tweet 1", "tweet 2", ...]"""

        try:
            message = self.client.chat.completions.create(
                model="GLM-4.5-Flash", # Using the same model as for LinkedIn posts
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse JSON response
            # The model might return text that needs to be extracted from message.content[0].text
            # and then parsed as JSON.
            response_text = message.choices[0].message.content
            # Attempt to find the JSON array within the response text
            json_start = response_text.find('[')
            json_end = response_text.rfind(']')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string = response_text[json_start : json_end + 1]
                tweets = json.loads(json_string)
            else:
                # Fallback if direct JSON parsing fails, try to split by common separators
                print("Warning: Direct JSON parsing failed for Twitter thread. Attempting fallback split.")
                tweets = [t.strip() for t in response_text.split('\n\n') if t.strip()]
                # Further refine to ensure each is a tweet
                if not all(isinstance(t, str) for t in tweets):
                    raise ValueError("Fallback split did not result in list of strings.")

            # Validate length
            validated_tweets = []
            for i, tweet in enumerate(tweets):
                if len(tweet) <= 280:
                    validated_tweets.append(f"{i+1}/{len(tweets)} {tweet}")
                else:
                    # Truncate if too long
                    validated_tweets.append(f"{i+1}/{len(tweets)} {tweet[:270]}...")

            return validated_tweets

        except Exception as e:
            print(f"Error generating Twitter thread: {e}")
            return [f"Error: Could not convert LinkedIn post to Twitter thread. {e}"]

    def generate_twitter_calendar(self, content_calendar):
        """
        Convert entire content calendar to Twitter threads

        Args:
            content_calendar (list): List of LinkedIn posts with metadata

        Returns:
            list: List of Twitter threads with metadata
        """
        twitter_calendar = []

        for item in content_calendar:
            if item['platform'] == 'linkedin': # Ensure we only process LinkedIn posts
                tweets = self.linkedin_to_twitter(item['content'])

                twitter_calendar.append({
                    'post_number': item['post_number'],
                    'topic': item['topic'],
                    'tweets': tweets,
                    'publish_date': item['publish_date'],
                    'platform': 'twitter',
                    'status': 'draft'
                })
            else:
                # Optionally handle other platforms or skip
                pass

        return twitter_calendar

if __name__ == "__main__":
    # Example usage (requires a sample LinkedIn post)
    sample_linkedin_post = """
    **The Future of AI in Content Creation: Efficiency Meets Authenticity**

    AI isn't just automating content creation—it's reshaping how we ideate, produce, and distribute. We're seeing three key trends:
    1. Hyper-Personalization at Scale: AI analyzes data to tailor content (from emails to video scripts) to individual audiences in real-time, boosting engagement.
    2. Multimodal Mastery: Generative AI blends text, images, audio, and video, enabling dynamic content experiences across platforms.
    3. Human-AI Collaboration: The most forward-thinking teams use AI for ideation, research, and optimization, freeing creators to focus on strategy and emotional resonance.

    **Career Implications:**
    - Upskilling is non-negotiable: Master prompt engineering, data interpretation, and ethical AI use.
    - New roles emerge: AI Content Strategists, Prompt Engineers, and AI Ethics Auditors are becoming critical.
    - Creativity evolves: AI handles execution; humans lead storytelling, brand voice, and nuanced messaging.

    **Business Insights:**
    - Efficiency gains: Reduce production time by 30-50% for routine content.
    - Risk alert: Over-reliance risks generic outputs. Authenticity and brand integrity require human oversight.

    **The future isn't AI *or* humans—it's AI *with* humans.** How is your team balancing AI efficiency with human creativity? Share your insights below!

    #AIinContentCreation #FutureOfWork #ContentMarketing #DigitalTransformation #CareerDevelopment #TechTrends #HumanCenteredAI
    """

    generator = TwitterThreadGenerator()
    tweets = generator.linkedin_to_twitter(sample_linkedin_post)
    for tweet in tweets:
        print(tweet)
