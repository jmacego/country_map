# __init__.py
from flask import Flask
from .views import views_blueprint

def create_app():
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Register blueprints
    app.register_blueprint(views_blueprint)

    return app
