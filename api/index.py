import os
import sys

# Ensure root directory is in sys.path so app imports work seamlessly on Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

env_name = os.environ.get("FLASK_ENV", "production")
app = create_app(env_name)
