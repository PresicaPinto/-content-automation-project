#!/usr/bin/env python3
"""
Production Entry Point for Ardelis Technologies Content Automation
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv('config/.env.production')

from flask import Flask
from core.config import settings
# from web.routes import main_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Validate configuration
    try:
        if settings.validate():
            print("✅ Configuration validated successfully")
        else:
            print("❌ Configuration validation failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Register blueprints
    # app.register_blueprint(main_bp)

    @app.route('/')
    def home():
        return """
        <h1>Ardelis Content Automation System</h1>
        <p>Welcome to the content automation platform!</p>
        <p>Available features:</p>
        <ul>
            <li>LinkedIn post generation</li>
            <li>Twitter thread generation</li>
            <li>Content scheduling</li>
        </ul>
        <p>Use the command line interface to generate content:</p>
        <pre>
python main.py linkedin_batch [num_posts]
python main.py twitter_batch
python main.py schedule_posts
        </pre>
        """

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app

def main():
    """Main entry point"""
    print("🚀 Starting Ardelis Content Automation System")
    print("=" * 50)

    # Create app
    app = create_app()

    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_ENV') == 'development'

    if debug:
        print("🔧 Running in development mode")
    else:
        print("🏭 Running in production mode")

    print(f"🌐 Server: http://{host}:{port}")
    print("=" * 50)

    # Start server
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()