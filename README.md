# Content Automation Project

This project automates the generation of social media content for LinkedIn and Twitter, and provides a framework for scheduling these posts.

## Features

- **LinkedIn Post Generation**: Generate professional and insightful LinkedIn posts based on predefined topics.
- **Twitter Thread Generation**: Create engaging Twitter threads from generated LinkedIn posts.
- **Content Scheduling (Planned)**: Integrate with Buffer to schedule posts across platforms.
- **Configurable**: Easily manage topics, output directories, and API keys.
- **Robust Error Handling**: Includes error handling for file operations and data processing.

## Project Structure

```
content_automation_project/
├── core/
│   ├── __init__.py
│   ├── ai_client.py
│   └── config.py
├── generators/
│   ├── __init__.py
│   ├── linkedin_generator.py
│   └── twitter_generator.py
├── outputs/
│   ├── content_calendar.json
│   └── twitter_calendar.json
├── prompts/
│   └── platform_prompts.py
├── tests/
│   ├── test_linkedin_generator.py
│   └── test_twitter_generator.py
├── .env
├── main.py
├── README.md
├── requirements.txt
├── scheduler.py
└── topics.json
```

- `core/`: Contains core functionalities like AI client integration and configuration.
- `generators/`: Houses the content generation logic for different social media platforms.
- `outputs/`: Stores the generated content calendars.
- `prompts/`: Defines the prompt templates used for content generation.
- `tests/`: Contains unit tests for various modules.
- `.env`: Environment variables for API keys and sensitive information.
- `main.py`: The main entry point for running content generation and scheduling tasks.
- `README.md`: Project documentation.
- `requirements.txt`: Lists project dependencies.
- `scheduler.py`: Handles scheduling of posts to social media platforms (e.g., Buffer).
- `topics.json`: Defines the topics and ideas for content generation.

## Setup

### 1. Clone the repository

```bash
git clone <repository_url>
cd content_automation_project
```

### 2. Create a virtual environment and install dependencies

It is recommended to use a virtual environment to manage project dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```
ZAI_API_KEY="your_zai_api_key"
BUFFER_ACCESS_TOKEN="your_buffer_access_token"
```

- `ZAI_API_KEY`: Your API key for the AI content generation service.
- `BUFFER_ACCESS_TOKEN`: Your access token for Buffer API (for scheduling).

### 4. Define Content Topics

Edit the `topics.json` file to define the topics and points you want to generate content about. The structure should be an array of objects, each with a `topic`, `points`, and `style`.

```json
[
  {
    "topic": "The Future of AI in Content Creation",
    "points": [
      "AI tools are transforming content workflows",
      "Personalization at scale is now possible"
    ],
    "style": "educational"
  }
]
```

## Usage

Navigate to the project's root directory in your terminal and activate your virtual environment:

```bash
cd /path/to/your/content_automation_project
source venv/bin/activate
```

### Generate LinkedIn Posts

To generate LinkedIn posts, run the `main.py` script with the `linkedin_batch` command. You can optionally specify the number of posts to generate.

```bash
python main.py linkedin_batch [num_posts]
# Example: python main.py linkedin_batch 5
```

### Generate Twitter Threads

To generate Twitter threads from the existing LinkedIn posts, run the `main.py` script with the `twitter_batch` command.

```bash
python main.py twitter_batch
```

### Schedule Posts

To schedule the generated posts to Buffer, run the `main.py` script with the `schedule_posts` command. This will prompt you to select Buffer profiles.

```bash
python main.py schedule_posts
```

## Running Tests

To run the unit tests, execute the following command from the project root:

```bash
python -m unittest discover tests
```

## Logging

Logs are generated in `app.log` file in the root directory of the project.

## Contributing

Feel free to fork the repository, open issues, or submit pull requests.
