import os
import sys
import json
import logging
from generators.linkedin_generator import LinkedInGenerator
from generators.twitter_generator import TwitterThreadGenerator
from scheduler import SocialMediaScheduler # Import the new scheduler

# Ensure ZAI_API_KEY and BUFFER_ACCESS_TOKEN are loaded from .env
# (This is handled by core/ai_client.py and scheduler.py respectively, but main.py needs to ensure .env is loaded)
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

def run_linkedin_generation(num_posts: int = None):
    logger.info("Starting LinkedIn post generation.")
    generator = LinkedInGenerator()
    posts = generator.generate_linkedin_posts(num_posts=num_posts)
    if posts:
        logger.info(f"Successfully generated {len(posts)} LinkedIn posts.")
    else:
        logger.warning("No LinkedIn posts were generated.")
    return posts

def run_twitter_generation(linkedin_calendar: list = None):
    logger.info("Starting Twitter thread generation.")
    if linkedin_calendar is None:
        # If no LinkedIn calendar is provided, try to load from file
        try:
            with open(os.path.join("outputs", "content_calendar.json"), 'r') as f:
                linkedin_calendar = json.load(f)
            logger.info("Loaded LinkedIn calendar from file for Twitter generation.")
        except FileNotFoundError:
            logger.error("Error: LinkedIn content_calendar.json not found. Please run LinkedIn generation first.")
            return

    generator = TwitterThreadGenerator()
    twitter_calendar = generator.generate_twitter_calendar(linkedin_calendar)

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    twitter_output_file_path = os.path.join(output_dir, "twitter_calendar.json")

    with open(twitter_output_file_path, 'w') as f:
        json.dump(twitter_calendar, f, indent=2)

    logger.info(f"Twitter calendar saved to {twitter_output_file_path}")
    logger.info(f"Generated {len(twitter_calendar)} Twitter threads.")
    return twitter_calendar

def run_scheduling():
    logger.info("Starting post scheduling.")
    BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")

    if not BUFFER_ACCESS_TOKEN:
        logger.error("BUFFER_ACCESS_TOKEN not found in environment variables. Please set it in your .env file.")
        raise ValueError("BUFFER_ACCESS_TOKEN not found in environment variables. Please set it in your .env file.")

    scheduler = SocialMediaScheduler(BUFFER_ACCESS_TOKEN)

    # Get profiles to allow user to select
    profiles = scheduler.get_profiles()
    if not profiles:
        logger.error("Could not retrieve Buffer profiles. Please check your access token and internet connection.")
        print("Could not retrieve Buffer profiles. Please check your access token and internet connection.")
        return

    print("\nAvailable Buffer Profiles:")
    for i, p in enumerate(profiles):
        print(f"{i+1}. {p['service'].capitalize()} ({p['service_display_name']}): ID={p['id']}")

    linkedin_profile_id = input("Enter LinkedIn Profile ID (from above list): ").strip()
    twitter_profile_id = input("Enter Twitter Profile ID (from above list): ").strip()

    if not linkedin_profile_id or not twitter_profile_id:
        logger.warning("Profile IDs cannot be empty. Aborting scheduling.")
        print("Profile IDs cannot be empty. Aborting scheduling.")
        return

    # Load content calendars
    try:
        with open(os.path.join("outputs", "content_calendar.json"), 'r') as f:
            linkedin_calendar = json.load(f)
        with open(os.path.join("outputs", "twitter_calendar.json"), 'r') as f:
            twitter_calendar = json.load(f)
        logger.info("Loaded content calendars for scheduling.")
    except FileNotFoundError:
        logger.error("Error: Content calendars not found. Please run content generation first.")
        print("Error: Content calendars not found. Please run content generation first.")
        return

    # Schedule LinkedIn posts
    linkedin_schedule_results = scheduler.schedule_content_calendar(linkedin_calendar, linkedin_profile_id)
    logger.info("LinkedIn scheduling results: %s", json.dumps(linkedin_schedule_results, indent=2))
    print("\n--- LinkedIn Scheduling Results ---")
    print(json.dumps(linkedin_schedule_results, indent=2))

    # Schedule Twitter threads
    twitter_schedule_results = scheduler.schedule_twitter_threads(twitter_calendar, twitter_profile_id)
    logger.info("Twitter scheduling results: %s", json.dumps(twitter_schedule_results, indent=2))
    print("\n--- Twitter Scheduling Results ---")
    print(json.dumps(twitter_schedule_results, indent=2))

    logger.info("Scheduling complete.")
    print("\n--- Scheduling Complete ---")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python main.py <command> [options]")
        print("Usage: python main.py <command> [options]")
        print("Commands:")
        print("  linkedin_batch [num_posts] - Generate LinkedIn posts in batch.")
        print("  twitter_batch              - Generate Twitter threads from existing LinkedIn posts.")
        print("  schedule_posts             - Schedule generated posts to Buffer.")
        sys.exit(1)

    command = sys.argv[1]

    if command == "linkedin_batch":
        num_posts = int(sys.argv[2]) if len(sys.argv) > 2 else None
        run_linkedin_generation(num_posts=num_posts)
    elif command == "twitter_batch":
        run_twitter_generation()
    elif command == "schedule_posts":
        run_scheduling()
    else:
        logger.error(f"Unknown command: {command}")
        print(f"Unknown command: {command}")
        sys.exit(1)