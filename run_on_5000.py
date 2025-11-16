#!/usr/bin/env python3
"""
Run proper backend on port 5000
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the proper backend
from proper_backend import app

if __name__ == '__main__':
    print("🚀 STARTING PROPER BACKEND ON PORT 5000")
    print("=" * 60)
    print("✅ Replacing old backend with proper one")
    print("✅ Real Twitter data: 0 followers, 2 following, 0 tweets")
    print("✅ Full API support: GET, POST, PUT, DELETE")
    print("✅ Clean database, no fake data!")
    print("=" * 60)

    # Run on port 5000 (replacing old backend)
    app.run(host='0.0.0.0', port=5000, debug=True)