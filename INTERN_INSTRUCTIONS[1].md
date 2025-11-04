# Intern Instructions - Build the Automation Machine
*Mission: Help build €100,000 in revenue in 90 days*

**Your Role:** Build automation tools that generate leads and content automatically.

---

## THE MISSION

We're building an automated lead generation and content machine for Ardelis Technologies.

**Goal:** Generate €100,000+ in consulting revenue in 90 days.

**How:** Automate content creation, lead research, and outreach so Merryl can focus ONLY on sales calls and closing deals.

**Your Impact:** Your automation will generate 10x more leads than manual work could ever achieve.

---

## TEAM STRUCTURE

### Intern 1: Content Automation Machine
**Your Mission:** Automate content creation and social media presence
**Time:** 4 hours/day, 5 days/week = 20 hours/week
**Tools You'll Build:**
1. LinkedIn content generator
2. Twitter repurposing bot
3. Content scheduling system
4. Metrics tracking dashboard

### Intern 2: Lead Generation Machine
**Your Mission:** Automate lead research and outreach
**Time:** 4 hours/day, 5 days/week = 20 hours/week
**Tools You'll Build:**
1. Company research automation
2. LinkedIn outreach automation
3. Email outreach system
4. CRM/Pipeline tracker

---

## WEEK 1: SETUP & PLANNING (October 14-18)

### Day 1 (Monday, Oct 14) - Both Interns

**Morning: Onboarding (4 hours both)**

**Task 1: Understand the Business (90 min)**
- [ ] Read this entire document
- [ ] Read START_HERE.md (understand the goal)
- [ ] Read 90_DAY_EXECUTION_ROADMAP.md (see the timeline)

**Task 2: Environment Setup (90 min)**
- [ ] Set up development environment:
  - Python 3.11+
  - Virtual environment (venv)
  - Git for version control
  - Code editor (VS Code recommended)
  - Access to shared Git repo

**Task 3: Install Core Libraries (60 min)**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core libraries
pip install requests beautifulsoup4 selenium
pip install anthropic openai  # For AI APIs
pip install pandas numpy
pip install flask  # For simple web interfaces
pip install schedule  # For scheduling tasks
```

**Task 4: Meet with Merryl (30 min)**
- Video call to understand requirements
- Ask questions
- Get API keys and credentials

---

## INTERN 1: CONTENT AUTOMATION MACHINE

### Your Tech Stack
- **Python** (main language)
- **Anthropic Claude API** or **OpenAI API** (content generation)
- **Buffer API** or **Hootsuite API** (scheduling)
- **Canva API** (optional - for graphics)
- **SQLite** or **PostgreSQL** (store content)

### Week 1: Build Content Generator

#### Day 1 (Mon, Oct 14) - Afternoon (4 hours)

**Project 1: LinkedIn Content Generator**

**Requirements:**
- Input: Bullet points or topic ideas
- Output: Formatted LinkedIn post (1500-2000 characters)
- Tone: Professional, authoritative, insightful
- Style: Hook → Story/Insight → Value → CTA

**Implementation:**

```python
# content_generator.py

import anthropic
import os
from datetime import datetime

class ContentGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    def generate_linkedin_post(self, topic, bullet_points, style="educational"):
        """
        Generate a LinkedIn post from bullet points

        Args:
            topic (str): Main topic/title
            bullet_points (list): List of key points
            style (str): "educational", "story", "case_study", "insight"

        Returns:
            str: Formatted LinkedIn post
        """

        prompt = f"""You are a LinkedIn content expert writing for Merryl D'Mello,
who builds agentic AI systems for European businesses.

Topic: {topic}

Key points to cover:
{chr(10).join(f"- {point}" for point in bullet_points)}

Write a LinkedIn post with this structure:
1. Hook (1-2 compelling lines)
2. Main content (insights, story, or value)
3. Call to action

Style: {style}
Tone: Professional, authoritative, but conversational
Length: 300-400 words
Format: Short paragraphs, use line breaks for readability

Do NOT use emojis unless specifically requested.
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def save_to_database(self, post, metadata):
        """Save generated post to database"""
        # TODO: Implement database saving
        pass

# Example usage
if __name__ == "__main__":
    generator = ContentGenerator()

    topic = "AI Health Coach - What I Learned"
    points = [
        "Built AI health coach that monitors 24/7",
        "Tracks diet, exercise, sleep patterns",
        "Like having personal trainer + nutritionist",
        "Cost: $0/month vs $500/month human equivalent",
        "This is what agentic AI can do for businesses"
    ]

    post = generator.generate_linkedin_post(topic, points, style="story")
    print(post)
```

**Your Tasks Day 1:**
- [ ] Set up the basic structure above
- [ ] Test with 3 sample topics
- [ ] Show results to Merryl for approval
- [ ] Iterate based on feedback

**Deliverable:** Working script that generates LinkedIn posts from bullet points.

---

#### Day 2 (Tue, Oct 15) - 4 hours

**Project 2: Content Templates & Batch Generation**

**Goal:** Create templates for different post types and batch generate 20 posts.

**Post Types to Support:**
1. Educational (40%) - Teaching concepts
2. Case Study (30%) - Sharing results from projects
3. Personal Story (20%) - Building in public
4. Industry Insight (10%) - Hot takes and trends

```python
# templates.py

class ContentTemplates:

    EDUCATIONAL_TEMPLATE = """
Hook: [Surprising fact or common misconception]

Most people think [wrong belief].

Here's what actually matters:

1. [Key insight 1]
2. [Key insight 2]
3. [Key insight 3]

Why this matters:
[Business impact]

[Call to action]
"""

    CASE_STUDY_TEMPLATE = """
Hook: [Impressive result]

[Company/Project type] was spending [time/money] on [process].

We built an agentic AI system that:
→ [Feature 1]
→ [Feature 2]
→ [Feature 3]

Result: [Specific outcome with numbers]

The key lesson: [Main takeaway]

[Call to action]
"""

    STORY_TEMPLATE = """
Hook: [Relatable opening]

[Year] - I was [situation]

[Key problem or challenge]

Then [turning point]

[What changed]

Now: [Current state]

The lesson: [Insight]

[Call to action]
"""

    def get_template(self, post_type):
        templates = {
            "educational": self.EDUCATIONAL_TEMPLATE,
            "case_study": self.CASE_STUDY_TEMPLATE,
            "story": self.STORY_TEMPLATE
        }
        return templates.get(post_type, self.EDUCATIONAL_TEMPLATE)
```

**Batch Generation:**

```python
# batch_generator.py

from content_generator import ContentGenerator
import json
from datetime import datetime, timedelta

class BatchContentGenerator:
    def __init__(self):
        self.generator = ContentGenerator()

    def generate_content_calendar(self, topics_file, num_days=30):
        """
        Generate content calendar for next N days

        Args:
            topics_file (str): JSON file with topic ideas
            num_days (int): Number of days to generate content for

        Returns:
            list: List of posts with metadata
        """

        # Load topics
        with open(topics_file, 'r') as f:
            topics = json.load(f)

        content_calendar = []

        for i in range(num_days):
            # Get topic for this day
            topic = topics[i % len(topics)]

            # Generate post
            post = self.generator.generate_linkedin_post(
                topic=topic['topic'],
                bullet_points=topic['points'],
                style=topic['style']
            )

            # Calculate publish date
            publish_date = datetime.now() + timedelta(days=i)

            content_calendar.append({
                'post_number': i + 1,
                'topic': topic['topic'],
                'content': post,
                'publish_date': publish_date.strftime('%Y-%m-%d'),
                'platform': 'linkedin',
                'status': 'draft'
            })

        return content_calendar

    def save_calendar(self, calendar, filename='content_calendar.json'):
        """Save content calendar to file"""
        with open(filename, 'w') as f:
            json.dump(calendar, f, indent=2)

# Example topics.json structure:
"""
[
  {
    "topic": "AI Health Coach - What I Learned",
    "points": [
      "Built AI health coach that monitors 24/7",
      "Tracks diet, exercise, sleep patterns"
    ],
    "style": "story"
  },
  {
    "topic": "Agentic AI vs Regular AI",
    "points": [
      "Regular AI: You ask, it answers",
      "Agentic AI: It acts, learns, improves"
    ],
    "style": "educational"
  }
]
"""
```

**Your Tasks Day 2:**
- [ ] Create `topics.json` with 30 topic ideas (Merryl will provide 10, you expand to 30)
- [ ] Build batch generator
- [ ] Generate 20 LinkedIn posts
- [ ] Save to `content_calendar.json`
- [ ] Show to Merryl for review

**Deliverable:** 20 ready-to-publish LinkedIn posts in JSON format.

---

#### Day 3 (Wed, Oct 16) - 4 hours

**Project 3: Twitter/X Thread Generator**

**Goal:** Auto-convert LinkedIn posts to Twitter threads (5-10 tweets).

**Twitter Format:**
- Tweet 1: Hook (must grab attention)
- Tweets 2-8: Content (one point per tweet)
- Tweet 9: Summary/Key takeaway
- Tweet 10: CTA + link

```python
# twitter_generator.py

class TwitterThreadGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

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

Return as JSON array: ["tweet 1", "tweet 2", ...]
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse JSON response
        import json
        tweets = json.loads(message.content[0].text)

        # Validate length
        validated_tweets = []
        for i, tweet in enumerate(tweets):
            if len(tweet) <= 280:
                validated_tweets.append(f"{i+1}/{len(tweets)} {tweet}")
            else:
                # Truncate if too long
                validated_tweets.append(f"{i+1}/{len(tweets)} {tweet[:270]}...")

        return validated_tweets

    def generate_twitter_calendar(self, content_calendar):
        """Convert entire content calendar to Twitter threads"""
        twitter_calendar = []

        for item in content_calendar:
            if item['platform'] == 'linkedin':
                tweets = self.linkedin_to_twitter(item['content'])

                twitter_calendar.append({
                    'post_number': item['post_number'],
                    'topic': item['topic'],
                    'tweets': tweets,
                    'publish_date': item['publish_date'],
                    'platform': 'twitter',
                    'status': 'draft'
                })

        return twitter_calendar
```

**Your Tasks Day 3:**
- [ ] Build Twitter thread generator
- [ ] Convert all 20 LinkedIn posts to Twitter threads
- [ ] Test that all tweets are under 280 characters
- [ ] Save to `twitter_calendar.json`
- [ ] Show to Merryl

**Deliverable:** 20 Twitter threads ready to post.

---

#### Day 4 (Thu, Oct 17) - 4 hours

**Project 4: Scheduling System**

**Goal:** Auto-schedule posts to LinkedIn and Twitter.

**Options:**
1. Use Buffer API (recommended - easier)
2. Use Hootsuite API
3. Build custom scheduler with direct posting

**Recommended: Buffer API**

```python
# scheduler.py

import requests
import json
from datetime import datetime, timedelta

class SocialMediaScheduler:
    def __init__(self, buffer_access_token):
        self.buffer_token = buffer_access_token
        self.base_url = "https://api.bufferapp.com/1"

    def get_profiles(self):
        """Get all connected social media profiles"""
        url = f"{self.base_url}/profiles.json"
        params = {'access_token': self.buffer_token}

        response = requests.get(url, params=params)
        return response.json()

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

        response = requests.post(url, data=data)
        return response.json()

    def schedule_content_calendar(self, content_calendar, linkedin_profile_id):
        """Schedule entire content calendar"""
        results = []

        for item in content_calendar:
            # Parse scheduled date
            publish_date = datetime.strptime(item['publish_date'], '%Y-%m-%d')
            # Set publish time (e.g., 9 AM)
            publish_date = publish_date.replace(hour=9, minute=0)

            result = self.schedule_post(
                profile_id=linkedin_profile_id,
                text=item['content'],
                scheduled_at=publish_date
            )

            results.append({
                'post_number': item['post_number'],
                'topic': item['topic'],
                'scheduled': result.get('success', False),
                'buffer_id': result.get('id', None)
            })

        return results

    def schedule_twitter_threads(self, twitter_calendar, twitter_profile_id):
        """Schedule Twitter threads (multiple tweets)"""
        results = []

        for item in twitter_calendar:
            publish_date = datetime.strptime(item['publish_date'], '%Y-%m-%d')
            publish_date = publish_date.replace(hour=14, minute=0)  # 2 PM

            # Schedule each tweet in thread with 2-min gaps
            for i, tweet in enumerate(item['tweets']):
                tweet_time = publish_date + timedelta(minutes=i*2)

                result = self.schedule_post(
                    profile_id=twitter_profile_id,
                    text=tweet,
                    scheduled_at=tweet_time
                )

            results.append({
                'post_number': item['post_number'],
                'topic': item['topic'],
                'tweets_scheduled': len(item['tweets'])
            })

        return results

# Usage
"""
# 1. Get Buffer access token from: https://buffer.com/developers/api
# 2. Get profile IDs
scheduler = SocialMediaScheduler(buffer_access_token='your_token')
profiles = scheduler.get_profiles()

# Find LinkedIn and Twitter profile IDs
linkedin_id = [p['id'] for p in profiles if p['service'] == 'linkedin'][0]
twitter_id = [p['id'] for p in profiles if p['service'] == 'twitter'][0]

# 3. Schedule content
linkedin_results = scheduler.schedule_content_calendar(content_calendar, linkedin_id)
twitter_results = scheduler.schedule_twitter_threads(twitter_calendar, twitter_id)
"""
```

**Alternative: Simple CSV Export for Manual Scheduling**

If Buffer API is complex, create CSV that can be uploaded to Buffer manually:

```python
# csv_exporter.py

import csv
from datetime import datetime

class ContentExporter:
    def export_to_csv(self, content_calendar, filename='content_schedule.csv'):
        """Export content calendar to CSV for manual upload"""

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Time', 'Platform', 'Content', 'Topic'])

            for item in content_calendar:
                writer.writerow([
                    item['publish_date'],
                    '09:00',  # 9 AM
                    item['platform'],
                    item['content'],
                    item['topic']
                ])
```

**Your Tasks Day 4:**
- [ ] Choose approach: Buffer API or CSV export
- [ ] If Buffer API: Get access token, test posting
- [ ] If CSV: Create CSV exporter
- [ ] Schedule/Export all 20 LinkedIn posts
- [ ] Schedule/Export all 20 Twitter threads
- [ ] Verify in Buffer dashboard

**Deliverable:** All content scheduled or ready for upload.

---

#### Day 5 (Fri, Oct 18) - 4 hours

**Project 5: Metrics Dashboard**

**Goal:** Track performance of all posts (views, likes, comments, shares).

**Simple Version: CSV Logger**

```python
# metrics_tracker.py

import csv
from datetime import datetime

class MetricsTracker:
    def __init__(self, csv_file='metrics.csv'):
        self.csv_file = csv_file
        self._init_csv()

    def _init_csv(self):
        """Initialize CSV with headers"""
        try:
            with open(self.csv_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Platform', 'Post_Number', 'Topic',
                    'Views', 'Likes', 'Comments', 'Shares', 'Engagement_Rate'
                ])
        except FileExistsError:
            pass

    def log_metrics(self, platform, post_number, topic, views, likes, comments, shares):
        """Log metrics for a post"""
        engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0

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

    def get_summary(self):
        """Get summary statistics"""
        # TODO: Implement analytics
        pass

# Manual usage (Merryl will input numbers daily/weekly):
"""
tracker = MetricsTracker()

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
"""
```

**Simple Web Interface (Optional):**

```python
# metrics_dashboard.py (Flask app)

from flask import Flask, render_template, request, jsonify
import csv

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Show metrics dashboard"""
    # Read metrics from CSV
    metrics = []
    with open('metrics.csv', 'r') as f:
        reader = csv.DictReader(f)
        metrics = list(reader)

    return render_template('dashboard.html', metrics=metrics)

@app.route('/add_metric', methods=['POST'])
def add_metric():
    """Add new metric entry"""
    data = request.json

    tracker = MetricsTracker()
    tracker.log_metrics(
        platform=data['platform'],
        post_number=data['post_number'],
        topic=data['topic'],
        views=data['views'],
        likes=data['likes'],
        comments=data['comments'],
        shares=data['shares']
    )

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

**Your Tasks Day 5:**
- [ ] Build metrics tracker (CSV-based is fine)
- [ ] Optional: Build simple web interface
- [ ] Document how Merryl should input metrics
- [ ] Test with dummy data
- [ ] Create dashboard view

**Deliverable:** Working metrics tracking system.

---

### INTERN 1 SUMMARY - Week 1

**What You Built:**
1. ✅ LinkedIn content generator (AI-powered)
2. ✅ Twitter thread repurposer
3. ✅ Content calendar (20 LinkedIn + 20 Twitter posts)
4. ✅ Scheduling system (Buffer or CSV)
5. ✅ Metrics tracker

**Output:**
- 40 pieces of content ready
- System to generate unlimited content
- Tracking in place

**Next Week:** Optimization, engagement automation, case study creation

---

## INTERN 2: LEAD GENERATION MACHINE

### Your Tech Stack
- **Python** (main language)
- **BeautifulSoup** + **Selenium** (web scraping)
- **Requests** (HTTP)
- **SQLite** or **PostgreSQL** (database)
- **SMTP** (email sending)
- **LinkedIn API** (if available, otherwise automation)

### Week 1: Build Lead Generation Tools

#### Day 1 (Mon, Oct 14) - Afternoon (4 hours)

**Project 1: Company Research Automation**

**Goal:** Build a scraper that researches target companies automatically.

**Data to Collect:**
- Company name
- Industry
- Size (employee count, revenue estimate)
- Location
- Website
- Decision maker (name, title, LinkedIn)
- Recent news/projects
- Pain points (from website)

**Implementation:**

```python
# company_scraper.py

import requests
from bs4 import BeautifulSoup
import json
from dataclasses import dataclass
import time

@dataclass
class Company:
    name: str
    industry: str
    size: str
    location: str
    website: str
    decision_maker: dict
    recent_news: list
    pain_points: list

class CompanyResearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_company_website(self, company_name):
        """Find company website via Google search"""
        # Use Google search or alternative
        search_url = f"https://www.google.com/search?q={company_name}+official+website"

        # TODO: Implement search and extract first result
        # For now, return placeholder
        return f"https://www.{company_name.lower().replace(' ', '')}.com"

    def scrape_company_website(self, url):
        """Extract information from company website"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract key information
            about_text = self._find_about_section(soup)
            services = self._find_services(soup)

            return {
                'about': about_text,
                'services': services
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def _find_about_section(self, soup):
        """Find 'About Us' section"""
        # Look for common patterns
        about_keywords = ['about', 'über uns', 'company', 'unternehmen']

        for keyword in about_keywords:
            section = soup.find(text=lambda t: keyword.lower() in t.lower() if t else False)
            if section:
                return section.parent.get_text(strip=True)[:500]

        return "No about section found"

    def _find_services(self, soup):
        """Extract services/products"""
        # TODO: Implement service extraction
        return []

    def find_decision_maker(self, company_name):
        """Find decision maker on LinkedIn"""
        # This would use LinkedIn scraping (be careful with rate limits)
        # For now, return structure

        return {
            'name': 'TBD',
            'title': 'Managing Director',
            'linkedin_url': 'TBD',
            'email': 'TBD'
        }

    def research_company(self, company_name):
        """Complete company research"""
        print(f"Researching: {company_name}")

        # Step 1: Find website
        website = self.search_company_website(company_name)
        time.sleep(2)  # Rate limiting

        # Step 2: Scrape website
        website_data = self.scrape_company_website(website)

        # Step 3: Find decision maker
        decision_maker = self.find_decision_maker(company_name)

        # Step 4: Compile data
        company = Company(
            name=company_name,
            industry='TBD',  # Would extract from website
            size='TBD',
            location='Germany',  # Would extract
            website=website,
            decision_maker=decision_maker,
            recent_news=[],
            pain_points=[]
        )

        return company

# Usage
researcher = CompanyResearcher()
company = researcher.research_company("SAP AG")
print(json.dumps(company.__dict__, indent=2))
```

**Better Approach: Use Existing APIs**

If scraping is too complex, use APIs:
- **Clearbit API** - Company enrichment
- **Hunter.io** - Email finding
- **Apollo.io** - B2B data

```python
# api_researcher.py

import requests

class APIResearcher:
    def __init__(self, clearbit_key, hunter_key):
        self.clearbit_key = clearbit_key
        self.hunter_key = hunter_key

    def enrich_company(self, domain):
        """Get company data from Clearbit"""
        url = f"https://company.clearbit.com/v2/companies/find"
        params = {'domain': domain}
        headers = {'Authorization': f'Bearer {self.clearbit_key}'}

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        return None

    def find_email(self, domain, first_name, last_name):
        """Find email using Hunter.io"""
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': self.hunter_key
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data['data']['email']
        return None
```

**Your Tasks Day 1:**
- [ ] Decide approach: Scraping or APIs
- [ ] If scraping: Build basic scraper for 5 test companies
- [ ] If APIs: Sign up for free tiers, test
- [ ] Store results in JSON file
- [ ] Show to Merryl

**Deliverable:** System that can research 1 company and extract key data.

---

#### Day 2 (Tue, Oct 15) - 4 hours

**Project 2: Batch Company Research + Database**

**Goal:** Research 100 companies and store in database.

```python
# database.py

import sqlite3
from datetime import datetime

class LeadDatabase:
    def __init__(self, db_file='leads.db'):
        self.db_file = db_file
        self._init_database()

    def _init_database(self):
        """Create tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                industry TEXT,
                size TEXT,
                location TEXT,
                website TEXT,
                decision_maker_name TEXT,
                decision_maker_title TEXT,
                decision_maker_email TEXT,
                decision_maker_linkedin TEXT,
                pain_points TEXT,
                status TEXT DEFAULT 'not_contacted',
                added_date TEXT,
                last_contact_date TEXT,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                interaction_type TEXT,
                date TEXT,
                notes TEXT,
                outcome TEXT,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_company(self, company):
        """Add company to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO companies (
                name, industry, size, location, website,
                decision_maker_name, decision_maker_title,
                decision_maker_email, decision_maker_linkedin,
                pain_points, added_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company['name'],
            company.get('industry', ''),
            company.get('size', ''),
            company.get('location', ''),
            company.get('website', ''),
            company.get('decision_maker', {}).get('name', ''),
            company.get('decision_maker', {}).get('title', ''),
            company.get('decision_maker', {}).get('email', ''),
            company.get('decision_maker', {}).get('linkedin', ''),
            ','.join(company.get('pain_points', [])),
            datetime.now().strftime('%Y-%m-%d')
        ))

        conn.commit()
        conn.close()

    def get_companies_by_status(self, status='not_contacted'):
        """Get companies filtered by status"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM companies WHERE status = ?', (status,))
        companies = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return companies

    def update_status(self, company_id, new_status, notes=''):
        """Update company status"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE companies
            SET status = ?, last_contact_date = ?, notes = ?
            WHERE id = ?
        ''', (new_status, datetime.now().strftime('%Y-%m-%d'), notes, company_id))

        conn.commit()
        conn.close()
```

**Batch Researcher:**

```python
# batch_researcher.py

from company_scraper import CompanyResearcher
from database import LeadDatabase
import time

class BatchResearcher:
    def __init__(self):
        self.researcher = CompanyResearcher()
        self.db = LeadDatabase()

    def research_companies(self, company_list_file):
        """
        Research multiple companies from a list

        Args:
            company_list_file (str): Text file with company names (one per line)
        """
        # Read company list
        with open(company_list_file, 'r') as f:
            companies = [line.strip() for line in f if line.strip()]

        print(f"Researching {len(companies)} companies...")

        for i, company_name in enumerate(companies):
            print(f"\n[{i+1}/{len(companies)}] {company_name}")

            try:
                # Research company
                company_data = self.researcher.research_company(company_name)

                # Save to database
                self.db.add_company(company_data.__dict__)

                print(f"✓ Added to database")

                # Rate limiting
                time.sleep(5)  # 5 seconds between requests

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        print(f"\n✓ Research complete! {len(companies)} companies processed.")

# Usage
"""
# 1. Create companies.txt file with company names:
# SAP AG
# Siemens AG
# BMW Group
# etc...

# 2. Run batch research
batch = BatchResearcher()
batch.research_companies('companies.txt')

# 3. Query database
db = LeadDatabase()
not_contacted = db.get_companies_by_status('not_contacted')
print(f"Companies to contact: {len(not_contacted)}")
"""
```

**Your Tasks Day 2:**
- [ ] Build database schema
- [ ] Build batch researcher
- [ ] Create `companies.txt` with 100 German company names (Merryl will help)
- [ ] Run batch research (this will take time due to rate limiting)
- [ ] Verify data in database
- [ ] Export to CSV for Merryl to review

**Deliverable:** Database with 100 researched companies.

---

#### Day 3 (Wed, Oct 16) - 4 hours

**Project 3: LinkedIn Outreach Automation**

**Goal:** Auto-send LinkedIn connection requests with personalized messages.

**IMPORTANT:** LinkedIn has rate limits. Stay within:
- Max 100 connections/week
- Max 20/day recommended
- Highly personalized messages

```python
# linkedin_automation.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

class LinkedInAutomation:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None

    def login(self):
        """Login to LinkedIn"""
        self.driver = webdriver.Chrome()  # or Firefox
        self.driver.get('https://www.linkedin.com/login')

        # Wait for login form
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )

        # Enter credentials
        email_input.send_keys(self.email)
        self.driver.find_element(By.ID, 'password').send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for dashboard
        time.sleep(5)
        print("✓ Logged in to LinkedIn")

    def send_connection_request(self, profile_url, message=''):
        """Send connection request to a profile"""
        try:
            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(random.uniform(3, 5))  # Random delay

            # Click "Connect" button
            connect_button = self.driver.find_element(By.XPATH, '//button[contains(., "Connect")]')
            connect_button.click()

            time.sleep(2)

            # Check if message option appears
            try:
                add_note_button = self.driver.find_element(By.XPATH, '//button[contains(., "Add a note")]')
                add_note_button.click()
                time.sleep(1)

                # Enter message
                message_box = self.driver.find_element(By.ID, 'custom-message')
                message_box.send_keys(message)

                # Send
                send_button = self.driver.find_element(By.XPATH, '//button[contains(., "Send")]')
                send_button.click()

                print(f"✓ Connection request sent with message")

            except:
                # No message option, just send
                send_button = self.driver.find_element(By.XPATH, '//button[contains(., "Send")]')
                send_button.click()
                print(f"✓ Connection request sent (no message)")

            time.sleep(random.uniform(5, 10))  # Random delay
            return True

        except Exception as e:
            print(f"✗ Error sending connection: {e}")
            return False

    def bulk_connect(self, profiles, message_template):
        """Send connection requests to multiple profiles"""
        success_count = 0

        for i, profile in enumerate(profiles):
            if i >= 20:  # Daily limit
                print(f"\n⚠ Reached daily limit (20 connections)")
                break

            print(f"\n[{i+1}/{len(profiles)}] {profile['name']}")

            # Personalize message
            message = message_template.format(
                name=profile['name'].split()[0],  # First name
                company=profile['company']
            )

            # Send request
            success = self.send_connection_request(profile['linkedin_url'], message)

            if success:
                success_count += 1

            # Random delay between requests
            time.sleep(random.uniform(30, 60))  # 30-60 sec between connections

        print(f"\n✓ Sent {success_count} connection requests")
        return success_count

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

# Message template
MESSAGE_TEMPLATE = """Hi {name},

I came across {company} while researching companies in [industry].

I help companies like yours automate [process] using agentic AI systems.

Would love to connect and share insights!

Best,
Merryl"""

# Usage (run this daily)
"""
from database import LeadDatabase

# Get companies to contact
db = LeadDatabase()
companies = db.get_companies_by_status('not_contacted')[:20]  # Get 20

# Prepare profiles
profiles = [
    {
        'name': c['decision_maker_name'],
        'company': c['name'],
        'linkedin_url': c['decision_maker_linkedin']
    }
    for c in companies if c['decision_maker_linkedin']
]

# Send connections
automation = LinkedInAutomation(email='your_email', password='your_password')
automation.login()
automation.bulk_connect(profiles, MESSAGE_TEMPLATE)
automation.close()

# Update database
for c in companies[:20]:
    db.update_status(c['id'], 'contacted_linkedin', 'Connection request sent')
"""
```

**SAFER ALTERNATIVE: Manual with Automation Assist**

If LinkedIn automation is risky, build a helper tool:

```python
# linkedin_helper.py

from database import LeadDatabase
import pyperclip  # For clipboard

class LinkedInHelper:
    def __init__(self):
        self.db = LeadDatabase()

    def get_next_person_to_contact(self):
        """Get next person to contact"""
        companies = self.db.get_companies_by_status('not_contacted', limit=1)

        if not companies:
            print("No more companies to contact!")
            return None

        company = companies[0]

        # Generate personalized message
        message = self._generate_message(company)

        # Copy to clipboard
        pyperclip.copy(message)

        # Display info
        print(f"\n{'='*50}")
        print(f"Company: {company['name']}")
        print(f"Person: {company['decision_maker_name']} ({company['decision_maker_title']})")
        print(f"LinkedIn: {company['decision_maker_linkedin']}")
        print(f"\n{'='*50}")
        print("Message (copied to clipboard):")
        print(f"{'='*50}")
        print(message)
        print(f"{'='*50}\n")

        input("Press Enter after sending connection request...")

        # Mark as contacted
        self.db.update_status(company['id'], 'contacted_linkedin', 'Manual connection sent')
        print("✓ Marked as contacted\n")

        return company

    def _generate_message(self, company):
        """Generate personalized message"""
        first_name = company['decision_maker_name'].split()[0]

        message = f"""Hi {first_name},

I came across {company['name']} while researching companies in {company['industry']}.

I help companies like yours automate operations using agentic AI systems.

Would love to connect and share insights!

Best,
Merryl"""

        return message

    def session(self, count=20):
        """Run a connection session"""
        print(f"Starting LinkedIn connection session ({count} connections)\n")

        for i in range(count):
            print(f"[{i+1}/{count}]")
            company = self.get_next_person_to_contact()

            if not company:
                break

# Usage (MUCH SAFER)
"""
helper = LinkedInHelper()
helper.session(count=20)  # Send 20 connections

# You manually:
# 1. Read the output
# 2. Go to LinkedIn profile
# 3. Click Connect
# 4. Paste message (from clipboard)
# 5. Send
# 6. Press Enter in terminal
# 7. Repeat

# This takes ~20 min for 20 connections
# But zero risk of LinkedIn ban
"""
```

**Your Tasks Day 3:**
- [ ] Choose approach: Full automation (risky) or Helper tool (safe)
- [ ] Build chosen solution
- [ ] Test with 5 connections
- [ ] Show to Merryl
- [ ] Get approval before scaling

**Deliverable:** LinkedIn outreach system (automated or semi-automated).

---

#### Day 4 (Thu, Oct 17) - 4 hours

**Project 4: Email Outreach System**

**Goal:** Send personalized cold emails automatically.

```python
# email_outreach.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import LeadDatabase
import time

class EmailOutreach:
    def __init__(self, smtp_server, smtp_port, email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        self.db = LeadDatabase()

    def send_email(self, to_email, subject, body):
        """Send a single email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            print(f"✓ Email sent to {to_email}")
            return True

        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False

    def generate_email(self, company):
        """Generate personalized email"""
        first_name = company['decision_maker_name'].split()[0]

        subject = f"Quick question about {company['name']}"

        body = f"""Hi {first_name},

I came across {company['name']} while researching {company['industry']} companies in Germany.

I noticed [specific observation about their business].

I've been helping companies like yours reduce operational time by 70-80% using agentic AI systems.

Recent example: A {company['industry']} company was spending 40 hours/week on [process]. We automated it down to 5 hours/week.

Would a quick 15-minute call make sense to explore if something similar could work for {company['name']}?

Either way, happy to share the framework we use - no strings attached.

Best regards,
Merryl D'Mello
Ardelis Technologies
ardelistech.com"""

        return subject, body

    def bulk_email(self, max_emails=25):
        """Send bulk emails"""
        # Get companies to email
        companies = self.db.get_companies_by_status('contacted_linkedin')[:max_emails]

        if not companies:
            print("No companies ready for email outreach")
            return

        print(f"Sending emails to {len(companies)} companies...\n")

        sent_count = 0

        for i, company in enumerate(companies):
            if not company['decision_maker_email']:
                print(f"[{i+1}] Skipping {company['name']} - no email")
                continue

            print(f"[{i+1}/{len(companies)}] {company['name']}")

            # Generate email
            subject, body = self.generate_email(company)

            # Send
            success = self.send_email(
                company['decision_maker_email'],
                subject,
                body
            )

            if success:
                sent_count += 1
                # Update status
                self.db.update_status(company['id'], 'contacted_email', 'Cold email sent')

            # Rate limiting
            time.sleep(10)  # 10 sec between emails

        print(f"\n✓ Sent {sent_count} emails")

# Usage
"""
# Setup (use Gmail or professional email)
outreach = EmailOutreach(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    email='your_email@gmail.com',
    password='your_app_password'  # Use app password for Gmail
)

# Send emails
outreach.bulk_email(max_emails=25)
"""
```

**Email Best Practices:**
- Max 50 emails/day (Gmail limit)
- Highly personalized
- No spam words
- Clear unsubscribe
- Professional signature

**Your Tasks Day 4:**
- [ ] Build email outreach system
- [ ] Get SMTP credentials from Merryl
- [ ] Test with 3 emails (to yourself first)
- [ ] Send to 5 real prospects
- [ ] Monitor replies

**Deliverable:** Working email outreach system.

---

#### Day 5 (Fri, Oct 18) - 4 hours

**Project 5: CRM Dashboard**

**Goal:** Simple web dashboard to manage all leads.

```python
# crm_dashboard.py (Flask app)

from flask import Flask, render_template, request, jsonify
from database import LeadDatabase

app = Flask(__name__)
db = LeadDatabase()

@app.route('/')
def dashboard():
    """Main dashboard"""
    # Get statistics
    all_companies = db.get_all_companies()

    stats = {
        'total': len(all_companies),
        'not_contacted': len([c for c in all_companies if c['status'] == 'not_contacted']),
        'contacted_linkedin': len([c for c in all_companies if c['status'] == 'contacted_linkedin']),
        'contacted_email': len([c for c in all_companies if c['status'] == 'contacted_email']),
        'responded': len([c for c in all_companies if c['status'] == 'responded']),
        'call_booked': len([c for c in all_companies if c['status'] == 'call_booked'])
    }

    return render_template('dashboard.html', stats=stats, companies=all_companies[:50])

@app.route('/api/companies')
def get_companies():
    """API endpoint for companies"""
    status = request.args.get('status', 'all')

    if status == 'all':
        companies = db.get_all_companies()
    else:
        companies = db.get_companies_by_status(status)

    return jsonify(companies)

@app.route('/api/update_status', methods=['POST'])
def update_status():
    """Update company status"""
    data = request.json

    db.update_status(
        company_id=data['company_id'],
        new_status=data['status'],
        notes=data.get('notes', '')
    )

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
```

**Simple HTML Template:**

```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Lead Pipeline Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 30px; }
        .stat-card {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 8px;
            min-width: 150px;
        }
        .stat-number { font-size: 36px; font-weight: bold; color: #007bff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f4f4f4; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .not-contacted { background-color: #ffc107; }
        .contacted { background-color: #17a2b8; color: white; }
        .responded { background-color: #28a745; color: white; }
    </style>
</head>
<body>
    <h1>Lead Pipeline Dashboard</h1>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{{ stats.total }}</div>
            <div>Total Companies</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.not_contacted }}</div>
            <div>Not Contacted</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.contacted_linkedin }}</div>
            <div>LinkedIn Sent</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.contacted_email }}</div>
            <div>Email Sent</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.responded }}</div>
            <div>Responded</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.call_booked }}</div>
            <div>Calls Booked</div>
        </div>
    </div>

    <h2>Companies</h2>
    <table>
        <thead>
            <tr>
                <th>Company</th>
                <th>Contact</th>
                <th>Location</th>
                <th>Status</th>
                <th>Last Contact</th>
            </tr>
        </thead>
        <tbody>
            {% for company in companies %}
            <tr>
                <td>
                    <strong>{{ company.name }}</strong><br>
                    <small>{{ company.industry }}</small>
                </td>
                <td>
                    {{ company.decision_maker_name }}<br>
                    <small>{{ company.decision_maker_title }}</small>
                </td>
                <td>{{ company.location }}</td>
                <td>
                    <span class="status {{ company.status }}">
                        {{ company.status }}
                    </span>
                </td>
                <td>{{ company.last_contact_date or '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
```

**Your Tasks Day 5:**
- [ ] Build Flask dashboard
- [ ] Create HTML template
- [ ] Test with database
- [ ] Add basic styling
- [ ] Deploy locally for Merryl to access

**Deliverable:** Working CRM dashboard at http://localhost:5002

---

### INTERN 2 SUMMARY - Week 1

**What You Built:**
1. ✅ Company research automation
2. ✅ Lead database (100 companies)
3. ✅ LinkedIn outreach automation
4. ✅ Email outreach system
5. ✅ CRM dashboard

**Output:**
- 100 researched companies in database
- 20 LinkedIn connections sent
- 25 emails sent
- Dashboard to track everything

**Next Week:** Optimization, response tracking, more leads

---

## WEEK 2-4: OPTIMIZATION & SCALE

### Both Interns

**Week 2 Focus:**
- Optimize tools based on results
- A/B test content and messages
- Build follow-up sequences
- Improve personalization

**Week 3-4 Focus:**
- Scale to 200+ companies
- Automate follow-ups
- Track which segments convert best
- Build reporting dashboards

---

## DAILY CHECKLIST (After Week 1)

### Intern 1 (Content Machine) - Daily Routine

**Every Morning (30 min):**
- [ ] Check scheduled posts for today
- [ ] Monitor yesterday's posts (likes, comments)
- [ ] Respond to comments (as Merryl)

**Every Day (3.5 hours):**
- [ ] Generate 2 new posts (LinkedIn + Twitter)
- [ ] Work on 1 case study/week
- [ ] A/B test different hooks
- [ ] Update metrics

### Intern 2 (Lead Machine) - Daily Routine

**Every Morning (30 min):**
- [ ] Check CRM for new responses
- [ ] Flag urgent leads for Merryl

**Every Day (3.5 hours):**
- [ ] Research 5 new companies
- [ ] Send 20 LinkedIn connections (automated or semi-automated)
- [ ] Send 5 cold emails
- [ ] Update CRM statuses
- [ ] Track metrics

---

## SUCCESS METRICS

### Week 1
- [ ] Automation tools built and tested
- [ ] 20 LinkedIn posts ready
- [ ] 20 Twitter threads ready
- [ ] 100 companies in database
- [ ] 20 LinkedIn connections sent
- [ ] 10 emails sent

### Week 4
- [ ] 80 posts published total
- [ ] 200+ tweets published
- [ ] 200 companies in database
- [ ] 200 LinkedIn connections sent
- [ ] 50 emails sent
- [ ] 5-10 responses received
- [ ] 2-3 discovery calls booked

### Week 8
- [ ] Systems running smoothly
- [ ] First deal closed (€15-50k)
- [ ] 10+ discovery calls completed
- [ ] 5+ proposals sent

---

## TOOLS & RESOURCES

### For Both Interns

**Development:**
- Python 3.11+
- VS Code or PyCharm
- Git + GitHub
- Virtual environment

**APIs (Get keys from Merryl):**
- Anthropic Claude API
- Buffer API (content scheduling)
- Optional: Clearbit, Hunter.io, Apollo.io

**Infrastructure:**
- SQLite (local dev)
- PostgreSQL (production - optional)
- Flask (web apps)
- Selenium (browser automation)

---

## IMPORTANT NOTES

### Rate Limits & Safety

**LinkedIn:**
- Max 20 connection requests/day
- Use random delays
- Highly personalize messages
- Risk of account restriction if too aggressive

**Email:**
- Max 50 emails/day (Gmail)
- Always include unsubscribe
- Monitor spam complaints
- Use professional domain if possible

**Content:**
- No plagiarism
- Fact-check all claims
- Get Merryl's approval before posting

### Communication

**Daily Check-in (10 min):**
- Show what you built today
- Ask questions
- Get feedback

**Weekly Review (30 min):**
- Show metrics
- Discuss what's working
- Plan next week

### If You Get Stuck

1. Google it first
2. Check Stack Overflow
3. Ask Merryl
4. Simplify the approach

---

## YOUR IMPACT

If you build these tools well, you will:
- Generate 1000+ leads over 90 days
- Enable 20+ sales calls
- Help close €100,000+ in revenue
- Build a system that runs for years

**This automation will 10x the business.**

**Your €110/month cost will generate €100,000+ value.**

**That's a 900x ROI.**

---

## QUESTIONS?

Ask Merryl during onboarding call (October 14, 8 PM).

Come prepared with questions about:
- API keys and credentials
- Target company preferences
- Content tone and style
- Technical architecture decisions

---

**Let's build this automation machine and win the game! 🚀**
