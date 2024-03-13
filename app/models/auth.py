from flask import session, current_app, redirect, url_for
import json
import uuid
import os
from functools import wraps
from datetime import datetime, timedelta

def is_email_allowed(email, allowed_emails):
    """
    Check if the provided email is in the list of allowed emails.

    Args:
        email (str): The email address to check.
        allowed_emails (list): A list of email addresses that are allowed.

    Returns:
        bool: True if the email is allowed, False otherwise.
    """
    return email in allowed_emails

def require_email_authorization(f):
    """
    Decorator to check if the user is authorized based on their email.

    This decorator retrieves the user's email from the session and checks if it is in the list of allowed emails. If the email is not allowed, it redirects the user to the OAuth2 authorization route.

    Args:
        f (function): The Flask view function to decorate.

    Returns:
        function: The decorated view function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the application is running in development or staging
        if os.environ.get('FLASK_ENV') in ['development', 'staging']:
            # Bypass the authorization check
            return f(*args, **kwargs)
        
        email = session.get('email')
        allowed_emails = current_app.config['ALLOWED_EMAIL']
        if not is_email_allowed(email, allowed_emails):
            # Redirect to the authorization route if the email is not allowed
            return redirect(url_for('auth.oauth2_authorize', provider='google'))
        return f(*args, **kwargs)
    return decorated_function
