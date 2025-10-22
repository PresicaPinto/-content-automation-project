import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zai import ZaiClient # Correct import for zai-sdk
from prompts.platform_prompts import get_prompt
from twitter_generator import TwitterThreadGenerator # Import the new generator

load_dotenv() # Load environment variables from .env file

ZAI_API_KEY = os.getenv("ZAI_API_KEY")

if not ZAI_API_KEY:
    raise ValueError("ZAI_API_KEY not found in environment variables. Please set it in a .env file.")

# Initialize the Zai client globally for reuse
client = ZaiClient(api_key=ZAI_API_KEY)

def generate_content(prompt: str) -> str:
    """
    Generates content using the Z.AI API.
    """
    print(f"Generating content for prompt: {prompt[:50]}...")
    try:
        response = client.chat.completions.create(
            model="GLM-4.5-Flash", # Updated to a valid z.ai model name
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"Error: Could not generate content for prompt: {prompt}"

if __name__ == "__main__":
    # --- Day 2: LinkedIn Batch Content Generation ---
    try:
        with open("topics.json", 'r') as f:
            topics_data = json.load(f)
    except FileNotFoundError:
        print("Error: topics.json not found. Please create it with content ideas.")
        exit()

    linkedin_content_calendar = []
    base_date = datetime.now()

    print(f"\n--- Starting Batch Content Generation for {len(topics_data)} LinkedIn Posts ---")

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
        print(f"Generated post {i+1}/{len(topics_data)} for topic: {topic[:30]}...")

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    linkedin_output_file_path = os.path.join(output_dir, "content_calendar.json")

    with open(linkedin_output_file_path, 'w') as f:
        json.dump(linkedin_content_calendar, f, indent=2)

    print(f"\n--- LinkedIn Batch Content Generation Complete ---")
    print(f"Content calendar saved to {linkedin_output_file_path}")
    print(f"Generated {len(linkedin_content_calendar)} LinkedIn posts.")

    # --- Day 3: Twitter Thread Generation ---
    print(f"\n--- Starting Twitter Thread Generation ---")

    twitter_generator = TwitterThreadGenerator()
    twitter_content_calendar = twitter_generator.generate_twitter_calendar(linkedin_content_calendar)

    twitter_output_file_path = os.path.join(output_dir, "twitter_calendar.json")
    with open(twitter_output_file_path, 'w') as f:
        json.dump(twitter_content_calendar, f, indent=2)

    print(f"--- Twitter Thread Generation Complete ---")
    print(f"Twitter calendar saved to {twitter_output_file_path}")
    print(f"Generated {len(twitter_content_calendar)} Twitter threads.")



