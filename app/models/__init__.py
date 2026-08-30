from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Declarative Base class for typed SQLAlchemy ORM models."""
    pass

db = SQLAlchemy(model_class=Base)
