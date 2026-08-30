import os
import sys

# Make sure project root is on the path (needed when Vercel CWD is /var/task)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from app import create_app  # noqa: E402

app = create_app("production")
