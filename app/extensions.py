from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_migrate import Migrate
from app.extensions import db  # Assuming db is your SQLAlchemy instance

migrate = Migrate()