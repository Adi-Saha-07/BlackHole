from flask import Flask
from config import config_by_name
from app.models import db
from app.services.cache import init_cache

def create_app(config_name="default"):
    """Flask Application Factory."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_by_name[config_name])
    
    # Initialize Database
    db.init_app(flask_app)
    
    # Initialize Cache
    init_cache(flask_app)
    
    # Create DB tables
    with flask_app.app_context():
        from app.models.history import QueryLog  # noqa: F401
        db.create_all()
    
    # Register blueprints
    from app.routes import main_bp
    flask_app.register_blueprint(main_bp)
    
    return flask_app
