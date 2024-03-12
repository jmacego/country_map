from flask import Flask
from .views import views
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Fix nginx set proxy header
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Set the secret key for the application
    app.secret_key = os.getenv('FLASK_SECRET_KEY')

    app.config['ALLOWED_EMAIL'] = os.getenv('ALLOWED_EMAIL').split(",")

    # set up oauth providers
    app.config['OAUTH2_PROVIDERS'] = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    'google': {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },

    # GitHub OAuth 2.0 documentation:
    # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
    'github': {
        'client_id': os.environ.get('GITHUB_CLIENT_ID'),
        'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
            'email': lambda json: json[0]['email'],
        },
        'scopes': ['user:email'],
    },

    # Apple
    'apple': {
        'client_id': os.environ.get('APPLE_CLIENT_ID'),
        'client_secret': os.environ.get('APPLE_CLIENT_SECRET'),
        'authorize_url': 'https://appleid.apple.com/auth/authorize',
        'token_url': 'https://appleid.apple.com/auth/token',
        'userinfo': {
            'url': 'https://appleid.apple.com/auth/userinfo',
            'email': lambda json: json[0]['email'],
        },
        'scopes': ['email'],
    },
}

    # Register blueprints
    app.register_blueprint(views)

    return app
