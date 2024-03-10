from flask import session, current_app, redirect, url_for
import json
import uuid
from functools import wraps

# File path for the visited data file
visited_file_path = 'instance/visited.json'

# File path for the links data file
links_file_path = 'instance/links.json'

class VisitedData:
    @staticmethod
    def load_visited_data():
        with open(visited_file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_visited_data(data):
        with open(visited_file_path, 'w') as file:
            json.dump(data, file, indent=4)

class LinksData:
    @staticmethod
    def load_links_data():
        with open(links_file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_links_data(data):
        with open(links_file_path, 'w') as file:
            json.dump(data, file, indent=4)

def is_email_allowed(email, allowed_emails):
    """Check if the provided email is in the list of allowed emails."""
    return email in allowed_emails

# Decorator to check if user is authorized
def require_email_authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        email = session.get('email')
        allowed_emails = current_app.config['ALLOWED_EMAIL']
        if not is_email_allowed(email, allowed_emails):
            # Redirect to the authorization route if the email is not allowed
            return redirect(url_for('views.oauth2_authorize', provider='google'))
        return f(*args, **kwargs)
    return decorated_function