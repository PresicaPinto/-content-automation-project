import os
from dotenv import load_dotenv
from zai import ZaiClient

load_dotenv() # Load environment variables from .env file

ZAI_API_KEY = os.getenv("ZAI_API_KEY")

if not ZAI_API_KEY:
    raise ValueError("ZAI_API_KEY not found in environment variables. Please set it in a .env file.")

# Initialize the Zai client globally for reuse
client = ZaiClient(api_key=ZAI_API_KEY)

def generate_content(prompt: str, model: str = "GLM-4.5-Flash") -> str:
    """
    Generates content using the Z.AI API.
    """
    print(f"Generating content for prompt: {prompt[:50]}... (using model: {model})")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"Error: Could not generate content for prompt: {prompt}. Details: {e}"
