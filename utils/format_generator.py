#!/usr/bin/env python3
"""
Format-based content generation utility
Supports example-based, structure-based, and style-based content generation
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class FormatGenerator:
    """Handle content generation based on user-provided formats"""

    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    def generate_with_format(self, topic_data: Dict[str, Any], format_template: Dict[str, Any]) -> str:
        """Generate content based on the format template"""

        format_type = format_template.get('type', 'structure_based')

        if format_type == 'example_based':
            return self._generate_example_based(topic_data, format_template)
        elif format_type == 'structure_based':
            return self._generate_structure_based(topic_data, format_template)
        elif format_type == 'style_based':
            return self._generate_style_based(topic_data, format_template)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def _generate_example_based(self, topic_data: Dict[str, Any], format_template: Dict[str, Any]) -> str:
        """Generate content following example format"""

        example_content = format_template.get('example', '')
        if not example_content:
            raise ValueError("Example content is required for example-based generation")

        # Analyze the example
        format_analysis = self._analyze_content_format(example_content)

        # Create format-aware prompt
        prompt = f"""
        Analyze this content example and generate new content following the EXACT same format, tone, and structure:

        EXAMPLE FORMAT:
        {example_content}

        FORMAT ANALYSIS:
        - Tone: {format_analysis['tone']}
        - Structure: {format_analysis['structure']}
        - Length: {format_analysis['length']} words
        - Uses Emojis: {format_analysis['uses_emojis']}
        - Has Hashtags: {format_analysis['has_hashtags']}
        - Paragraphs: {format_analysis['paragraph_count']}

        TOPIC: {topic_data.get('topic', '')}
        KEY POINTS: {', '.join(topic_data.get('points', []))}
        PLATFORM: {topic_data.get('platform', 'LinkedIn')}

        INSTRUCTIONS:
        1. Match the exact tone and voice of the example
        2. Use the same paragraph structure and formatting
        3. Include similar elements (emojis, hashtags, bullet points if present)
        4. Maintain approximately the same length
        5. Generate professional content suitable for the platform
        6. Follow the same writing style (formal, casual, enthusiastic, etc.)

        Generate complete content now:
        """

        if self.ai_client:
            return self.ai_client.generate(prompt)
        else:
            # Fallback to basic generation
            return self._basic_format_generation(topic_data, format_analysis)

    def _generate_structure_based(self, topic_data: Dict[str, Any], format_template: Dict[str, Any]) -> str:
        """Generate content following defined structure"""

        structure = format_template.get('structure', {})
        topic = topic_data.get('topic', '')
        points = topic_data.get('points', [])
        platform = topic_data.get('platform', 'LinkedIn')

        # Build content based on structure
        content_parts = []

        # Hook/Opening
        if structure.get('hook', True):
            hook = self._generate_hook(topic, platform)
            content_parts.append(hook)

        # Main Content
        if points:
            if structure.get('bullets', True):
                # Bullet points format
                bullets = self._format_as_bullets(points, structure.get('data', False))
                content_parts.append(bullets)
            else:
                # Paragraph format
                paragraphs = self._format_as_paragraphs(points, structure.get('data', False))
                content_parts.extend(paragraphs)

        # Call to Action
        if structure.get('cta', True):
            cta = self._generate_cta(topic, platform)
            content_parts.append(cta)

        # Hashtags
        if structure.get('hashtags', True):
            hashtags = self._generate_hashtags(topic, platform)
            content_parts.append(hashtags)

        # Add emojis if requested
        if structure.get('emojis', False):
            content = '\n\n'.join(content_parts)
            return self._add_relevant_emojis(content, topic, platform)
        else:
            return '\n\n'.join(content_parts)

    def _generate_style_based(self, topic_data: Dict[str, Any], format_template: Dict[str, Any]) -> str:
        """Generate content following specific style"""

        style_config = format_template.get('style', {})
        tone = style_config.get('tone', 'professional')
        length = style_config.get('length', 'medium')
        notes = style_config.get('notes', '')

        topic = topic_data.get('topic', '')
        points = topic_data.get('points', [])
        platform = topic_data.get('platform', 'LinkedIn')

        # Create style-aware prompt
        prompt = f"""
        Generate content with these style requirements:

        STYLE CONFIGURATION:
        - Tone: {tone}
        - Length: {length}
        - Additional Notes: {notes}
        - Platform: {platform}

        TOPIC: {topic}
        KEY POINTS: {', '.join(points)}

        INSTRUCTIONS:
        1. Use {tone} tone throughout
        2. Target length: {self._get_word_count_target(length)} words
        3. Follow platform-specific guidelines for {platform}
        4. Incorporate all key points naturally
        5. {self._get_style_instructions(tone)}
        6. {notes if notes else ''}

        Generate professional content now:
        """

        if self.ai_client:
            return self.ai_client.generate(prompt)
        else:
            return self._basic_style_generation(topic_data, style_config)

    def _analyze_content_format(self, content: str) -> Dict[str, Any]:
        """Analyze content to extract format characteristics"""

        analysis = {
            'tone': self._detect_tone(content),
            'structure': self._detect_structure(content),
            'length': len(content.split()),
            'uses_emojis': bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)),
            'has_hashtags': bool(re.search(r'#\w+', content)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'has_bullets': bool(re.search(r'[•\-\*]\s', content)),
            'question_based': bool(re.search(r'\?', content)),
            'data_driven': bool(re.search(r'(\d+%|\d+ million|\d+ billion|statistics|research|study)', content, re.IGNORECASE))
        }

        return analysis

    def _detect_tone(self, content: str) -> str:
        """Detect the tone of the content"""

        content_lower = content.lower()

        # Professional indicators
        professional_words = ['research', 'analysis', 'strategy', 'implementation', 'professional', 'industry']

        # Casual indicators
        casual_words = ['hey', 'guys', 'awesome', 'cool', 'just', 'really', 'super']

        # Enthusiastic indicators
        enthusiastic_words = ['excited', 'amazing', 'incredible', 'fantastic', 'thrilled', 'wonderful']

        # Inspirational indicators
        inspirational_words = ['dream', 'inspire', 'motivation', 'success', 'journey', 'believe']

        scores = {
            'professional': sum(1 for word in professional_words if word in content_lower),
            'casual': sum(1 for word in casual_words if word in content_lower),
            'enthusiastic': sum(1 for word in enthusiastic_words if word in content_lower),
            'inspirational': sum(1 for word in inspirational_words if word in content_lower),
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'professional'

    def _detect_structure(self, content: str) -> str:
        """Detect the structure pattern of the content"""

        if re.search(r'[•\-\*]\s', content):
            return 'bullet_points'
        elif content.count('\n\n') >= 3:
            return 'multiple_paragraphs'
        elif re.search(r'\?', content):
            return 'question_based'
        elif re.search(r'#\w+', content):
            return 'social_media'
        else:
            return 'standard'

    def _generate_hook(self, topic: str, platform: str) -> str:
        """Generate an engaging hook"""

        hooks = [
            f"🚀 Exciting developments in {topic} are reshaping our industry!",
            f"💡 Here's what you need to know about {topic} right now...",
            f"🔥 The {topic} landscape is evolving rapidly. Are you ready?",
            f"📈 Latest insights on {topic} that can't be ignored...",
            f"⚡ Breaking down the {topic} trends that matter most..."
        ]

        # Select hook based on platform
        if platform.lower() == 'twitter':
            return hooks[0][:100] + "..." if len(hooks[0]) > 100 else hooks[0]
        else:
            return hooks[0]

    def _format_as_bullets(self, points: List[str], include_data: bool = False) -> str:
        """Format key points as bullet points"""

        bullets = []
        for i, point in enumerate(points[:5], 1):  # Limit to 5 points
            if include_data and i % 2 == 0:
                bullets.append(f"• {point} 📊 (Recent studies show 73% improvement)")
            else:
                bullets.append(f"• {point}")

        return '\n'.join(bullets)

    def _format_as_paragraphs(self, points: List[str], include_data: bool = False) -> List[str]:
        """Format key points as paragraphs"""

        paragraphs = []
        for i, point in enumerate(points[:3], 1):  # Limit to 3 paragraphs
            if include_data:
                paragraphs.append(f"{point} Research indicates that organizations embracing this approach see significant improvements in efficiency and outcomes.")
            else:
                paragraphs.append(f"{point}")

        return paragraphs

    def _generate_cta(self, topic: str, platform: str) -> str:
        """Generate call to action"""

        if platform.lower() == 'linkedin':
            return f"What are your thoughts on {topic}? Share your experiences in the comments below! 👇"
        elif platform.lower() == 'twitter':
            return f"What's your take on {topic}? Let me know! 🎯"
        else:
            return f"Join the conversation about {topic} and share your insights! ✨"

    def _generate_hashtags(self, topic: str, platform: str) -> str:
        """Generate relevant hashtags"""

        # Extract keywords from topic
        words = re.findall(r'\b\w+\b', topic.lower())
        hashtags = []

        # Add topic-based hashtags
        for word in words[:3]:  # Limit to 3 main keywords
            hashtags.append(f"#{word}")

        # Add platform-specific hashtags
        if platform.lower() == 'linkedin':
            hashtags.extend(["#ProfessionalDevelopment", "#IndustryInsights", "#ThoughtLeadership"])
        elif platform.lower() == 'twitter':
            hashtags.extend(["#trending", "#innovation", "#tech"])
        else:
            hashtags.extend(["#content", "#creativity", "#inspiration"])

        return '\n\n' + ' '.join(hashtags[:5])  # Limit to 5 hashtags

    def _add_relevant_emojis(self, content: str, topic: str, platform: str) -> str:
        """Add relevant emojis to content"""

        # Simple emoji mapping based on keywords
        emoji_mapping = {
            'technology': '💻',
            'ai': '🤖',
            'data': '📊',
            'growth': '📈',
            'innovation': '💡',
            'success': '🎯',
            'team': '👥',
            'future': '🔮',
            'digital': '🌐',
            'strategy': '♟️'
        }

        content_with_emojis = content

        for keyword, emoji in emoji_mapping.items():
            if keyword.lower() in topic.lower():
                # Add emoji at the beginning if not already present
                if emoji not in content_with_emojis:
                    content_with_emojis = f"{emoji} " + content_with_emojis
                break

        return content_with_emojis

    def _get_word_count_target(self, length: str) -> str:
        """Get target word count based on length preference"""

        length_map = {
            'short': '100-200',
            'medium': '200-400',
            'long': '400-600'
        }

        return length_map.get(length, '200-400')

    def _get_style_instructions(self, tone: str) -> str:
        """Get style-specific instructions"""

        style_instructions = {
            'professional': "Use formal language, industry terminology, and data-driven insights",
            'casual': "Use conversational language, friendly tone, and approachable style",
            'enthusiastic': "Use energetic language, exclamation points, and motivational tone",
            'authoritative': "Use expert language, confidence, and definitive statements",
            'conversational': "Use question-based approach, relatable examples, and engaging tone",
            'inspirational': "Use motivational language, future-focused perspective, and uplifting tone"
        }

        return style_instructions.get(tone, "Use clear, professional language")

    def _basic_format_generation(self, topic_data: Dict[str, Any], format_analysis: Dict[str, Any]) -> str:
        """Fallback basic generation when AI client is not available"""

        topic = topic_data.get('topic', '')
        points = topic_data.get('points', [])

        # Simple structured content based on analysis
        content_parts = []

        # Opening based on detected tone
        if format_analysis['tone'] == 'professional':
            content_parts.append(f"Industry insights on {topic} reveal significant opportunities for strategic advancement.")
        else:
            content_parts.append(f"Exciting developments in {topic} are worth exploring!")

        # Key points
        if points:
            if format_analysis.get('has_bullets'):
                for point in points[:3]:
                    content_parts.append(f"• {point}")
            else:
                for point in points[:2]:
                    content_parts.append(f"{point} This represents a key consideration for stakeholders.")

        # Closing
        content_parts.append("Share your thoughts and experiences in the comments.")

        return '\n\n'.join(content_parts)

    def _basic_style_generation(self, topic_data: Dict[str, Any], style_config: Dict[str, Any]) -> str:
        """Fallback basic style-based generation"""

        topic = topic_data.get('topic', '')
        points = topic_data.get('points', [])
        tone = style_config.get('tone', 'professional')

        content_parts = []

        # Tone-based opening
        openings = {
            'professional': f"Comprehensive analysis of {topic} highlights key strategic considerations.",
            'casual': f"Let's talk about {topic} - there's some interesting stuff happening!",
            'enthusiastic': f"Absolutely excited to share insights about {topic} with you all! 🎉",
            'inspirational': f"Transform your understanding of {topic} and unlock new possibilities! ✨"
        }

        content_parts.append(openings.get(tone, openings['professional']))

        # Add points
        for point in points[:3]:
            content_parts.append(f"• {point}")

        # Call to action
        ctas = {
            'professional': "Engage with this content to advance your industry knowledge.",
            'casual': "What do you think? Drop your thoughts below! 👇",
            'enthusiastic': "Join the conversation and let's make an impact together! 🚀",
            'inspirational': "Take the first step towards transformation and share your journey! 💫"
        }

        content_parts.append(ctas.get(tone, ctas['professional']))

        return '\n\n'.join(content_parts)