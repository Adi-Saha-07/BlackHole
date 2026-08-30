import os
import sys
import traceback

# Make sure project root is on the path (needed when Vercel CWD is /var/task)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from app import create_app
    app = create_app("production")
except Exception:
    _init_error = traceback.format_exc()

    def app(environ, start_response):
        status = "500 Internal Server Error"
        response_headers = [("Content-Type", "text/html; charset=utf-8")]
        start_response(status, response_headers)
        html = f"""<!DOCTYPE html>
<html>
<head><title>BlackHole Startup Error</title></head>
<body style="background:#0f1117;color:#f87171;font-family:monospace;padding:24px;line-height:1.5;">
    <h2 style="color:#fbbf24;">BlackHole Serverless Startup Error</h2>
    <p style="color:#94a3b8;">An error occurred while initializing the Flask application on Vercel:</p>
    <pre style="background:#1e222d;padding:16px;border-radius:8px;overflow:auto;color:#ef4444;border:1px solid #374151;">{_init_error}</pre>
</body>
</html>"""
        return [html.encode("utf-8")]

handler = app

