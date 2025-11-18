#!/bin/bash
# This script ensures that the correct virtual environment is activated
# and the full-featured server is started.

echo "Activating virtual environment..."
source /home/presica/playground/content_automation_project/venv/bin/activate

echo "Starting the Ardelis Content Automation System..."
python3 /home/presica/playground/content_automation_project/full_stack_dashboard.py