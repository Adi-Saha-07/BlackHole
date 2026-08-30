import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "cosmic-event-horizon-secret-key-42")
    
    # Google Custom Search API Configuration
    GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX = os.environ.get("GOOGLE_SEARCH_CX", "")

    # Gemini AI Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    
    # Redis Configuration
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TTL = int(os.environ.get("CACHE_DEFAULT_TTL", 600))  # 10 minutes
    
    # SQLite Database Configuration:
    # On Serverless platforms (Vercel / Lambda), filesystem is read-only except /tmp
    _db_env = os.environ.get("DATABASE_URL", "").strip()
    if _db_env:
        SQLALCHEMY_DATABASE_URI = _db_env
    else:
        _is_serverless = bool(
            os.environ.get("VERCEL")
            or os.environ.get("NOW_REGION")
            or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
            or os.environ.get("LAMBDA_TASK_ROOT")
        )
        if _is_serverless:
            SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/blackhole.db"
        else:
            try:
                _app_dir = os.path.abspath(os.path.dirname(__file__))
                _local_db = os.path.join(_app_dir, "blackhole.db")
                if os.access(_app_dir, os.W_OK):
                    SQLALCHEMY_DATABASE_URI = f"sqlite:///{_local_db}"
                else:
                    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/blackhole.db"
            except Exception:
                SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
