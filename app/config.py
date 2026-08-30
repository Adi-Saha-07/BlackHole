import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _safe_int(val, default):
    try:
        val_str = str(val if val is not None else "").strip()
        return int(val_str) if val_str else default
    except (ValueError, TypeError):
        return default


def _build_db_uri():
    db_env = os.environ.get("DATABASE_URL", "").strip()
    if db_env:
        return db_env
    # Detect serverless env (Vercel, AWS Lambda, etc.)
    if any([
        os.environ.get("VERCEL"),
        os.environ.get("NOW_REGION"),
        os.environ.get("AWS_LAMBDA_FUNCTION_NAME"),
        os.environ.get("LAMBDA_TASK_ROOT"),
    ]):
        return "sqlite:////tmp/blackhole.db"
    # Local dev — write next to this file's parent
    try:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(root, "blackhole.db")
        if os.access(root, os.W_OK):
            return f"sqlite:///{db_path}"
    except Exception:
        pass
    return "sqlite:////tmp/blackhole.db"


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "cosmic-event-horizon-secret-key-42")

    # Google Custom Search
    GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX = os.environ.get("GOOGLE_SEARCH_CX", "")

    # Gemini AI
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TTL = _safe_int(os.environ.get("CACHE_DEFAULT_TTL"), 600)

    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = _build_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
