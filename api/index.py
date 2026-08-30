import os
import sys
import traceback

# Ensure root directory is in sys.path so app imports work seamlessly on Vercel
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

def _make_error_app(message):
    """Returns a minimal WSGI app that shows the startup error."""
    def error_app(environ, start_response):
        body = (
            f"<h1>BlackHole Startup Error</h1><pre>{message}</pre>"
        ).encode("utf-8")
        start_response("500 Internal Server Error", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]
    return error_app

try:
    # Step 1: Import dotenv safely (no .env file exists on Vercel)
    try:
        from dotenv import load_dotenv
        load_dotenv()  # silently passes if .env doesn't exist
    except ImportError:
        pass

    # Step 2: Import the Flask app factory
    from app import create_app

    env_name = os.environ.get("FLASK_ENV", "production")
    app = create_app(env_name)
    handler = app

except Exception:
    _tb = traceback.format_exc()
    print("=== BLACKHOLE STARTUP CRASH ===", flush=True)
    print(_tb, flush=True)
    app = _make_error_app(_tb)
    handler = app
