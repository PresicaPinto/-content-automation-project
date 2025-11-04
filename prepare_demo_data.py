#!/usr/bin/env python3
"""
Demo Data Preparation Script
Generate impressive sample content for the presentation
"""

import json
import os
from datetime import datetime, timedelta
import random

def create_demo_content():
    """Create impressive demo content"""

    # Professional business topics
    topics = [
        "AI Transformation in Manufacturing",
        "Digital Supply Chain Optimization",
        "Sustainable Technology Solutions",
        "Cloud Migration Best Practices",
        "Data-Driven Decision Making",
        "Cybersecurity in Modern Business",
        "Industry 4.0 Implementation",
        "Business Process Automation",
        "Customer Experience Innovation",
        "Digital Strategy Consulting"
    ]

    # High-quality content templates
    content_templates = {
        "educational": [
            "🚀 Transforming {topic}: A Comprehensive Guide\n\nIn today's rapidly evolving business landscape, organizations that embrace {topic} are gaining significant competitive advantages. Our latest analysis reveals that companies implementing these strategies see 40% improvement in operational efficiency.\n\nKey insights:\n• 85% of industry leaders report increased productivity\n• ROI typically realized within 6-8 months\n• Scalable solutions for businesses of all sizes\n\nReady to accelerate your {topic} journey? Let's discuss how our expertise can drive your transformation.\n\n#DigitalTransformation #BusinessInnovation #TechLeadership",

            "💡 Strategic Insights: {topic}\n\nThe future of business is being reshaped by {topic}. Organizations that adapt now will dominate their markets tomorrow.\n\nOur research shows:\n• Market growth rate: 23% annually\n• Early adopters seeing 3x ROI\n• Critical for competitive advantage\n\nWe've helped 50+ companies successfully implement {topic} strategies. Our proven methodology ensures smooth transitions and measurable results.\n\nDM us for a complimentary strategy session.\n\n#BusinessStrategy #Innovation #GrowthMindset"
        ],
        "promotional": [
            "🎯 Unlock Your Business Potential with {topic}\n\nAre you leaving money on the table? Companies leveraging {topic} are outperforming competitors by 2.5x.\n\nOur tailored solutions deliver:\n✅ 40% cost reduction\n✅ 60% faster time-to-market\n✅ 3x customer satisfaction improvement\n\nLimited opportunity: We're taking on 3 new clients this quarter for our premium {topic} program.\n\nBook your free consultation: [Link] or DM STRATEGY\n\n#BusinessGrowth #Innovation #Consulting",

            "⚡ Results-Driven {topic} Solutions\n\nStop guessing, start growing. Our {topic} expertise has helped clients generate €2.5M+ in additional revenue.\n\nRecent wins:\n• Manufacturing client: €450K savings in Q3\n• Retail partner: 300% ROI in 90 days\n• Tech startup: Market entry 6 months ahead of schedule\n\nYour success story starts here. We guarantee results or you don't pay.\n\nLimited slots available. DM RESULTS to qualify.\n\n#BusinessSuccess #ROI #Transformation"
        ],
        "industry_insights": [
            "📊 Industry Report: {topic} Trends 2024\n\nLatest market analysis reveals {topic} is no longer optional—it's essential for survival.\n\nMarket intelligence:\n• €12.7B market size by 2025\n• 67% of companies plan increased investment\n• Skills gap affecting 80% of organizations\n\nOur proprietary framework addresses these challenges head-on. We're not just consultants; we're transformation partners.\n\nGet your complimentary industry assessment: DM REPORT\n\n#IndustryAnalysis #MarketTrends #StrategicPlanning",

            "🔍 Exclusive Insights: The {topic} Revolution\n\nBreaking: Our latest research uncovers critical {topic} trends that will separate winners from losers in 2024.\n\nShocking findings:\n• 90% of current strategies will be obsolete by 2025\n• AI-powered {topic} showing 400% better results\n• Traditional methods failing 73% of the time\n\nWe've developed the antidote. Our next-generation {topic} framework is delivering unprecedented results for early adopters.\n\nFirst-mover advantage expires soon. DM INSIGHTS for details.\n\n#FutureOfWork #Innovation #CompetitiveAdvantage"
        ]
    }

    demo_posts = []

    for i, topic in enumerate(topics):
        style = random.choice(list(content_templates.keys()))
        template = random.choice(content_templates[style])

        post = {
            "id": f"demo_post_{i+1:03d}",
            "topic": topic,
            "content": template.format(topic=topic),
            "platform": "linkedin",
            "style": style,
            "hashtags": "#DigitalTransformation #BusinessInnovation #TechLeadership",
            "scheduled_date": (datetime.now() + timedelta(days=i%7)).strftime('%Y-%m-%d'),
            "scheduled_time": f"{9 + (i%8):02d}:00",
            "status": "generated" if i > 3 else "published",
            "created_at": datetime.now().isoformat(),
            "engagement_predictions": {
                "expected_views": random.randint(800, 2000),
                "expected_likes": random.randint(25, 80),
                "expected_comments": random.randint(5, 20),
                "expected_shares": random.randint(2, 10)
            }
        }

        if post["status"] == "published":
            post["published_at"] = (datetime.now() - timedelta(days=random.randint(1, 5))).isoformat()
            post["actual_metrics"] = {
                "views": random.randint(500, 1500),
                "likes": random.randint(15, 60),
                "comments": random.randint(3, 15),
                "shares": random.randint(1, 8)
            }

        demo_posts.append(post)

    return demo_posts

def create_demo_metrics():
    """Create impressive demo metrics"""

    return {
        "total_content": 25,
        "total_views": 18750,
        "total_engagement": 892,
        "content_by_platform": {
            "linkedin": 20,
            "twitter": 5,
            "facebook": 0
        },
        "content_by_style": {
            "educational": 10,
            "promotional": 8,
            "industry_insights": 7
        },
        "performance_averages": {
            "views_per_post": 750,
            "engagement_rate": 4.8,
            "click_through_rate": 2.3
        },
        "business_impact": {
            "expected_leads": 375,
            "expected_demos": 38,
            "expected_deals": 8,
            "expected_revenue": 120000,
            "roi_multiple": 136
        },
        "growth_metrics": {
            "content_growth": 150,
            "engagement_growth": 200,
            "reach_growth": 180
        }
    }

def save_demo_data():
    """Save all demo data to files"""

    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)

    # Create and save demo posts
    demo_posts = create_demo_content()

    # Save to content calendar format
    with open('outputs/content_calendar.json', 'w') as f:
        json.dump(demo_posts, f, indent=2)

    # Save to fast generated format
    with open('outputs/fast_linkedin_demo.json', 'w') as f:
        json.dump(demo_posts[:10], f, indent=2)

    # Save metrics
    demo_metrics = create_demo_metrics()
    with open('outputs/demo_metrics.json', 'w') as f:
        json.dump(demo_metrics, f, indent=2)

    # Create content calendar for manual posting demo
    today = datetime.now().strftime('%Y-%m-%d')
    todays_posts = [post for post in demo_posts if post["scheduled_date"] == today or post["status"] == "published"]

    with open('outputs/todays_posts.json', 'w') as f:
        json.dump(todays_posts, f, indent=2)

    print("✅ Demo data created successfully!")
    print(f"📝 Generated {len(demo_posts)} demo posts")
    print(f"📊 Total expected views: {demo_metrics['total_views']:,}")
    print(f"💰 Expected revenue: €{demo_metrics['business_impact']['expected_revenue']:,}")
    print(f"🎯 ROI multiple: {demo_metrics['business_impact']['roi_multiple']}x")
    print(f"📅 Today's posts: {len(todays_posts)}")

    print("\n🎯 Demo is ready! Open http://localhost:5000/ to see the impressive results!")

if __name__ == '__main__':
    save_demo_data()