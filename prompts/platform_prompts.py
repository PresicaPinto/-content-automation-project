# platform_prompts.py

PLATFORM_PROMPTS = {
    "twitter": {
        "short_post": """
        Generate a concise and engaging tweet (max 280 characters) about the following topic.
        Include relevant hashtags and a call to action if appropriate.
        Topic: {topic}
        """,
        "thread_starter": """
        Generate the first tweet of a Twitter thread (max 280 characters) about the following topic.
        Make it hook the reader and indicate it's part of a thread.
        Topic: {topic}
        """
    },
    "linkedin": {
        "professional_post": """
        Draft a professional and insightful LinkedIn post (max 1300 characters) about the following topic.
        Focus on industry trends, career development, or business insights.
        Include a question to encourage engagement.
        Topic: {topic}
        """,
        "thought_leadership": """
        Write a thought-provoking LinkedIn post (max 1300 characters) that positions the author as a leader
        in the field. Discuss a challenge or opportunity related to the topic and offer a unique perspective.
        Topic: {topic}
        """
    },
    "instagram": {
        "engaging_caption": """
        Create an engaging Instagram caption (max 2200 characters, but aim for conciseness) for a visual post
        about the following topic. Use emojis, relevant hashtags, and a clear call to action or question.
        Focus on visual storytelling.
        Topic: {topic}
        """,
        "story_text": """
        Generate short, punchy text for an Instagram Story slide about the following topic.
        Keep it very brief and attention-grabbing.
        Topic: {topic}
        """
    }
}

def get_prompt(platform: str, prompt_type: str, topic: str) -> str:
    """
    Retrieves a specific prompt template and formats it with the given topic.
    """
    if platform not in PLATFORM_PROMPTS:
        raise ValueError(f"Platform '{platform}' not supported.")
    if prompt_type not in PLATFORM_PROMPTS[platform]:
        raise ValueError(f"Prompt type '{prompt_type}' not supported for platform '{platform}'.")

    template = PLATFORM_PROMPTS[platform][prompt_type]
    return template.format(topic=topic)

if __name__ == "__main__":
    # Example Usage
    topic = "The Future of AI in Content Creation"

    twitter_prompt = get_prompt("twitter", "short_post", topic)
    print(f"--- Twitter Short Post Prompt ---\n{twitter_prompt}\n")

    linkedin_prompt = get_prompt("linkedin", "professional_post", topic)
    print(f"--- LinkedIn Professional Post Prompt ---\n{linkedin_prompt}\n")

    instagram_prompt = get_prompt("instagram", "engaging_caption", topic)
    print(f"--- Instagram Engaging Caption Prompt ---\n{instagram_prompt}\n")
