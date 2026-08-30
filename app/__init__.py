import os
from flask import Flask
from config import config_by_name
from app.models import db
from app.services.cache import init_cache

def create_app(config_name="default"):
    """Flask Application Factory."""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )
    
    config_class = config_by_name.get(config_name, config_by_name["default"])
    flask_app.config.from_object(config_class)
    
    # Initialize Database safely
    try:
        db.init_app(flask_app)
        with flask_app.app_context():
            from app.models.history import QueryLog  # noqa: F401
            db.create_all()
    except Exception as e:
        flask_app.logger.warning(f"Database setup notice: {e}")
    
    # Initialize Cache
    try:
        init_cache(flask_app)
    except Exception as e:
        flask_app.logger.warning(f"Cache init notice: {e}")
    
    # Register blueprints
    from app.routes import main_bp
    flask_app.register_blueprint(main_bp)
    
    return flask_app
