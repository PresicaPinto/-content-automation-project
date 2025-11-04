import unittest
import os
import json
from generators.linkedin_generator import LinkedInGenerator
from core import config

class TestLinkedInGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = LinkedInGenerator()
        self.topics_file = config.TOPICS_FILE
        self.output_dir = config.OUTPUT_DIR
        self.output_file = os.path.join(self.output_dir, config.LINKEDIN_OUTPUT_FILE)

        # Create a dummy topics file
        self.dummy_topics = [
            {
                "topic": "Test Topic 1",
                "points": ["Point 1", "Point 2"],
                "style": "educational"
            },
            {
                "topic": "Test Topic 2",
                "points": ["Point 3", "Point 4"],
                "style": "case_study"
            }
        ]
        with open(self.topics_file, 'w') as f:
            json.dump(self.dummy_topics, f)

    def tearDown(self):
        if os.path.exists(self.topics_file):
            os.remove(self.topics_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_generate_linkedin_posts_returns_list(self):
        posts = self.generator.generate_linkedin_posts(num_posts=1)
        self.assertIsInstance(posts, list)
        self.assertEqual(len(posts), 1)

    def test_generate_linkedin_posts_file_not_found(self):
        os.remove(self.topics_file)
        posts = self.generator.generate_linkedin_posts()
        self.assertEqual(posts, [])

if __name__ == '__main__':
    unittest.main()
