from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for, session, make_response, session, current_app
from requests_oauthlib import OAuth2Session
import json
import uuid
import os
import secrets
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from urllib.parse import urlencode
from ..models.travel import VisitedData, LinksData
from ..models.auth import require_email_authorization
from ..models.misc import remaining_days

from app.travel import bp

# Load environment variables
load_dotenv()

@bp.route('/world')
@require_email_authorization
def world_map():
    """
    Display a world map with visited countries.

    This route handles the main page view of the application, where a world map highlighting visited countries is displayed. It requires email authorization before access is granted.

    Returns:
        render_template (flask.Response): A Flask response object that renders the 'visited_map.html' template with the title 'Visited World'.
    """
    return render_template('travel/visited_map.html', title='Visited World')

@bp.route('/states')
@require_email_authorization
def states():
    """
    Display a US map with visited states.

    This route serves the page that shows a map of the United States, highlighting the states that have been visited. Access to this page is restricted and requires email authorization before viewing.

    Returns:
        render_template (flask.Response): A Flask response object that renders the 'visited_map.html' template with the title 'Visited States'.
    """
    return render_template('travel/visited_map.html', title='Visited States')

@bp.route('/links')
@require_email_authorization
def links():
    """
    Display and modify a list of useful travel-related links.

    This route provides an interface for displaying and potentially modifying a curated list of travel-related links. It requires email authorization for access, ensuring that only authorized users can view or modify the links.

    Returns:
        render_template (flask.Response): A Flask response object that renders the 'links.html' template with the title 'Travel Links'.
    """
    return render_template('travel/links.html', title='Travel Links')

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
    return render_template('travel/daysleft.html', number_of_weekdays=number_of_weekdays,
                           months_remaining=months_remaining, days_remaining=days_remaining,
                           total_days_remaining=total_days_remaining,
                           start_date=start_date, end_date=end_date,
                           title='Days Left')

@bp.route('/api/visited', methods=['GET'])
@require_email_authorization
def get_visited():
    """
    Produces a JSON list of visited details.

    This endpoint returns a list of places (countries or states) and their visited status. The list can be filtered by the type of map ('world' or 'states') using the 'whichMap' query parameter.

    Args:
        whichMap (str, optional): A query parameter that determines which list to send. Defaults to 'world'.

    Returns:
        flask.Response: A JSON response containing an array of places with their visited status.
    """
    # Get the 'whichMap' query parameter from the URL
    which_map = request.args.get('whichMap', default='world', type=str).removeprefix('Visited ').lower()
    
    # Load the visited data from the file
    visited = VisitedData.load_visited_data()
    
    # Filter the visited data based on the 'which_map' key
    filtered_visited = [place for place in visited if place.get('which_map') == which_map]
    
    return jsonify(filtered_visited)


@bp.route('/api/visited/<uuid:visited_id>', methods=['GET'])
@require_email_authorization
def get_single_visited(visited_id):
    """
    Get details of a specific visited item by its ID.

    This endpoint retrieves the details of a particular visited place using its unique identifier. The endpoint is not intended for general use and requires email authorization for access.

    Args:
        visited_id (uuid.UUID): The unique identifier of the visited item.

    Returns:
        flask.Response: A JSON response containing the details of the visited item if found, or a 404 error if not found.
    """
    visited = VisitedData.load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    return jsonify(visited_entry) if visited_entry else ('', 404)


@bp.route('/api/visited', methods=['POST'])
@require_email_authorization
def add_or_update_visited():
    """
    Add a new visited place or update an existing one.

    This endpoint allows for the addition of a new visited place or the update of an existing place's details. It accepts a JSON payload with the visited place's details. If the place already exists (matched by name), it updates the existing entry. Otherwise, it creates a new entry with a unique UUID.

    Args:
        whichMap (str): A query parameter from the URL that specifies the map type ('world' or 'states').

    Returns:
        flask.Response: A JSON response containing the newly added or updated visited place details. Returns a 200 status code if an existing place was updated, or a 201 status code if a new place was added.
    """
    # Get the 'whichMap' query parameter from the URL
    visited = visited = VisitedData.load_visited_data()
    new_visited = request.json
    # Find if the country already exists in the data
    existing_country = next((item for item in visited if item['name'].lower() == new_visited['name'].lower()), None)
    
    if existing_country:
        # Update existing country data
        existing_country.update(new_visited)
    else:
        # Assign a new UUID and add the new country
        new_id = str(uuid.uuid4())
        new_visited['id'] = new_id
        visited.append(new_visited)
    
    VisitedData.save_visited_data(visited)
    return jsonify(new_visited), 200 if existing_country else 201

@bp.route('/api/visited/<uuid:visited_id>', methods=['PUT'])
@require_email_authorization
def update_visited(visited_id):
    """
    Update the details of a specific visited place.

    This endpoint allows for updating the details of a visited place identified by its UUID. If the visited place with the given ID does not exist, it returns a 404 error. Otherwise, it updates the place with the provided JSON payload.

    Args:
        visited_id (uuid.UUID): The unique identifier of the visited place to be updated.

    Returns:
        flask.Response: A JSON response containing the updated details of the visited place, or a 404 error if the place with the given ID does not exist.
    """
    visited = visited = VisitedData.load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    if not visited_entry:
        return ('', 404)
    update_data = request.json
    visited_entry.update(update_data)
    VisitedData.save_visited_data(visited)
    return jsonify(visited_entry)

@bp.route('/api/visited/<uuid:visited_id>', methods=['DELETE'])
@require_email_authorization
def delete_visited(visited_id):
    """
    Delete a visited place from the list by its UUID.

    This endpoint removes a visited place from the list based on its unique identifier. If the operation is successful, it returns a 204 No Content status, indicating that the item has been deleted.

    Args:
        visited_id (uuid.UUID): The unique identifier of the visited place to be deleted.

    Returns:
        flask.Response: An empty response with a 204 status code indicating successful deletion.
    """
    visited = visited = VisitedData.load_visited_data()
    visited = [item for item in visited if item['id'] != str(visited_id)]
    VisitedData.save_visited_data(visited)
    return ('', 204)

@bp.route('/api/links', methods=['GET'])
@require_email_authorization
def get_links():
    """
    Retrieve a list of useful travel-related links.

    This endpoint fetches a list of travel-related links that may be useful for users. Access to this list requires email authorization, ensuring that only authorized users can retrieve the data.

    Returns:
        flask.Response: A JSON response containing an array of travel-related links.
    """
    return jsonify(LinksData.load_links_data())

@bp.route('/api/links', methods=['POST'])
@require_email_authorization
def add_link():
    """
    Add a new link to the list of travel-related links.

    This endpoint accepts a JSON payload with the details of a new link and adds it to the existing list of links. Each new link is assigned a unique UUID and a position in the list. If notes are not provided in the payload, an empty string is assigned by default.

    Returns:
        flask.Response: A JSON response containing the details of the newly added link, with a 201 status code indicating successful creation.
    """
    links = LinksData.load_links_data()
    new_link = request.json
    new_link['id'] = str(uuid.uuid4())  # Generate a unique ID
    new_link['position'] = len(links) + 1  # Assign position
    new_link['notes'] = new_link.get('notes', '')  # Add notes field
    links.append(new_link)
    LinksData.save_links_data(links)
    return jsonify(new_link), 201

@bp.route('/api/links/<id>', methods=['PUT'])
@require_email_authorization
def update_link(id):
    """
    Update an existing link's details.

    This endpoint allows for updating the details of an existing link identified by its ID. If the link with the given ID does not exist, it returns a 404 error. Otherwise, it updates the link with the provided JSON payload, particularly the 'notes' field if specified.

    Args:
        id (str): The unique identifier of the link to be updated.

    Returns:
        flask.Response: A JSON response containing the updated link details, or a 404 error if the link with the given ID does not exist.
    """
    links = LinksData.load_links_data()
    link = next((l for l in links if l['id'] == id), None)
    if not link:
        return ('', 404)
    update_data = request.json
    link['notes'] = update_data.get('notes', link.get('notes', ''))  # Update notes field
    link.update(update_data)
    LinksData.save_links_data(links)
    return jsonify(link)

@bp.route('/api/links/<id>', methods=['DELETE'])
@require_email_authorization
def delete_link(id):
    """
    Delete a specific link from the list by its ID.

    This endpoint removes a link from the list of travel-related links using its unique identifier. If the operation is successful, it returns a 204 No Content status, indicating that the item has been deleted.

    Args:
        id (str): The unique identifier of the link to be deleted.

    Returns:
        flask.Response: An empty response with a 204 status code indicating successful deletion.
    """
    links = LinksData.load_links_data()
    links = [l for l in links if l['id'] != id]
    LinksData.save_links_data(links)
    return ('', 204)

