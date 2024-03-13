from flask import session, current_app, redirect, url_for
import json
import uuid
import os
from functools import wraps
from datetime import datetime, timedelta


# File path for the visited data file
visited_file_path = 'instance/visited.json'

# File path for the links data file
links_file_path = 'instance/links.json'

class VisitedData:
    """
    A class used to handle the loading and saving of visited data.

    This class provides static methods to load and save data related to visited places, such as countries or states, from a JSON file.
    """

    @staticmethod
    def load_visited_data():
        """
        Load visited data from a JSON file.

        This method reads from a file specified by 'visited_file_path' and loads the JSON data into memory.

        Returns:
            list: A list of dictionaries containing visited data.
        """
        with open(visited_file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_visited_data(data):
        """
        Save visited data to a JSON file.

        This method writes the provided data to a file specified by 'visited_file_path', formatting it with an indentation of 4 spaces for readability.

        Args:
            data (list): A list of dictionaries containing visited data to be saved.

        Returns:
            None
        """
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

def remaining_days(start_date, end_date, excluded_dates=None):
    """
    Calculate the number of weekdays between two dates, optionally excluding specific dates.

    :param start_date: The start date as a datetime object.
    :param end_date: The end date as a datetime object.
    :param excluded_dates: A list of dates to exclude in 'YYYY-MM-DD' format.
    :return: The number of weekdays between the start and end dates, excluding specified dates.
    """
    if excluded_dates is None:
        excluded_dates = []

    # Convert excluded dates from strings to datetime objects
    excluded_datetimes = [datetime.strptime(date, '%Y-%m-%d') for date in excluded_dates]

    # Generate a range of dates between the start and end dates
    date_generated = [start_date + timedelta(days=x) for x in range(0, (end_date-start_date).days)]

    # Filter out the weekdays and excluded dates
    weekdays = [date for date in date_generated if date.weekday() < 5 and date not in excluded_datetimes]

    # Return the number of weekdays
    return len(weekdays)

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
