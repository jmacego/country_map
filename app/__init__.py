from flask import Flask, render_template
import os
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from app.extensions import db

from app.auth import bp as auth_bp
from app.dates import bp as dates_bp
from app.travel import bp as travel_bp


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)

    # Fix nginx set proxy header
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dates_bp)
    app.register_blueprint(travel_bp)

    # Default page
    @app.route("/")
    def index_page():
        return render_template("base.html", title='Index')
    return app
