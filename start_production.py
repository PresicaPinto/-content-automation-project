#!/usr/bin/env python3
"""
Production Startup Script for Ardelis Technologies Content Automation
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import settings, Config
from full_stack_dashboard import app

def main():
    """Production main entry point"""
    print("🚀 Starting Ardelis Content Automation System")
    print("=" * 60)

    # Validate configuration
    print("🔧 Validating configuration...")
    if not Config.validate():
        print("❌ Configuration validation failed!")
        print("💡 Please fix the errors above and restart")
        sys.exit(1)

    # Ensure directories exist
    print("📁 Creating directories...")
    Config.ensure_directories()

    # Production settings
    print("⚙️  Production Configuration:")
    print(f"   Host: {settings.HOST}")
    print(f"   Port: {settings.PORT}")
    print(f"   Output Dir: {settings.OUTPUT_DIR}")
    print(f"   Log Level: {settings.LOG_LEVEL}")

    print("=" * 60)
    print("🏭 Starting production server...")
    print("🌐 Ardelis Content Automation is running!")
    print(f"📍 Access at: http://{settings.HOST}:{settings.PORT}")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)

    try:
        # Run production server
        app.run(
            host=settings.HOST,
            port=settings.PORT,
            debug=False
        )
    except KeyboardInterrupt:
        print("\n👋 Production server stopped by user")
    except Exception as e:
        print(f"❌ Production server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()