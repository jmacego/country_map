from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for, session, make_response, session, current_app
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from urllib.parse import urlencode
from ..models.misc import remaining_days

# Load environment variables
load_dotenv()
from app.dates import bp

@bp.route('/')
def test():
    return("test")

@bp.route('/daysleft')
def days_left():
    """
    Display the days remaining until Marcia finishes school, excluding specific dates.
    Also display the total number of months and days remaining from today until the end date.
    """
    # Define the start date (today) and the end date
    start_date = datetime.now()
    end_date = datetime(2024, 6, 17)

    # List of dates to exclude (format: 'YYYY-MM-DD')
    excluded_dates = ['2024-03-25', '2024-03-26', '2024-03-27', '2024-03-28', '2024-03-29',
                      '2024-03-30', '2024-03-31', '2024-04-01', '2024-04-02', '2024-04-03',
                      '2024-04-04', '2024-04-05', '2024-05-27']

    # Calculate the number of weekdays, excluding specific dates
    number_of_weekdays = remaining_days(start_date, end_date, excluded_dates)

    # Calculate the total number of months and days remaining
    delta = relativedelta(end_date, start_date)
    months_remaining = delta.months
    days_remaining = delta.days

    # Calculate the total number of days remaining without exclusions
    total_days_remaining = (end_date - start_date).days

    # Render a template with the result
    return render_template('daysleft.html', number_of_weekdays=number_of_weekdays,
                           months_remaining=months_remaining, days_remaining=days_remaining,
                           total_days_remaining=total_days_remaining,
                           start_date=start_date, end_date=end_date,
                           title='Days Left')

