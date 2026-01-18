"""
Application Entry Point
Medical Billing Validation System
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from app.models import db, create_tables

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        create_tables(app)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
