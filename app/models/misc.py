from flask import session, current_app, redirect, url_for
import json
import uuid
import os
from functools import wraps
from datetime import datetime, timedelta

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