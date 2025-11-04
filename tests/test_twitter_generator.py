import unittest
import os
import json
from generators.twitter_generator import TwitterThreadGenerator
from core import config

class TestTwitterGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = TwitterThreadGenerator()
        self.output_dir = config.OUTPUT_DIR
        self.output_file = os.path.join(self.output_dir, config.TWITTER_OUTPUT_FILE)

        # Create a dummy LinkedIn calendar
        self.dummy_linkedin_calendar = [
            {
                "post_number": 1,
                "topic": "Test Topic 1",
                "platform": "linkedin",
                "prompt_type": "professional_post",
                "content": "This is a test post.",
                "publish_date": "2025-10-27",
                "status": "draft"
            }
        ]

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_generate_twitter_calendar_returns_list(self):
        threads = self.generator.generate_twitter_calendar(self.dummy_linkedin_calendar)
        self.assertIsInstance(threads, list)
        self.assertEqual(len(threads), 1)

    def test_generate_twitter_calendar_empty_linkedin_calendar(self):
        threads = self.generator.generate_twitter_calendar([])
        self.assertEqual(threads, [])

if __name__ == '__main__':
    unittest.main()
