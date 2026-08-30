import os
try:
    from dotenv import load_dotenv
    # Automatically load environment variables from .env file
    load_dotenv()
except ImportError:
    pass

from app import create_app

env_name = "production" if os.environ.get("VERCEL") else os.environ.get("FLASK_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT") or 5000)
    except (ValueError, TypeError):
        port = 5000
    app.run(host="0.0.0.0", port=port, debug=True)
