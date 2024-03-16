from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for, session, make_response, session, current_app, abort
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
from ..models.travel import Visited, Links
from ..models.auth import require_email_authorization

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
    visited = Visited.load_visited_data()
    
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
    visited = Visited.load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    return jsonify(visited_entry) if visited_entry else ('', 404)


@bp.route('/api/visited', methods=['POST'])
@require_email_authorization
def add_or_update_visited():
    """
    Add a new visited place or update an existing one.

    This endpoint allows for the addition of a new visited place or the update
    of an existing place's details. It accepts a JSON payload with the visited
    place's details.

    Returns:
        flask.Response: A JSON response containing the newly added or updated
        visited place details. Returns a 201 status code if a new place was
        added.
    """
    data = request.get_json()
    if not data or not data.get('name') or not data.get('which_map'):
        abort(400, description="Missing required data")

    new_visited = Visited.add_new_entry(
        name=data['name'],
        john=data.get('john', False),
        marcia=data.get('marcia', False),
        todo=data.get('todo', False),
        which_map=data['which_map']
    )
    return jsonify(new_visited.to_dict()), 201

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
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    id = data['id']
    updated_entry = Visited.update_entry(str(id), data)
    if updated_entry:
        return jsonify(updated_entry.to_dict()), 200
    else:
        abort(404, description="Visited entry not found")

@bp.route('/api/visited/<uuid:visited_id>', methods=['DELETE'])
@require_email_authorization
def delete_visited(visited_id):
    """
    Delete a visited place from the list by its UUID.

    This endpoint removes a visited place from the list based on its unique
    identifier. If the operation is successful, it returns a 204 No Content
    status, indicating that the item has been deleted.

    Args:
        visited_id (uuid.UUID): The unique identifier of the visited place to
        be deleted.

    Returns:
        flask.Response: An empty response with a 200 status code indicating
        successful deletion.
    """
def delete_visited(id):
    if Visited.delete_by_id(str(id)):
        return jsonify({'message': 'Visited entry deleted successfully', 'id': str(id)}), 200
    else:
        abort(404, description="Visited entry not found")

@bp.route('/api/links', methods=['GET'])
@require_email_authorization
def get_links():
    """
    Retrieve a list of useful travel-related links.

    This endpoint fetches a list of travel-related links that may be useful for users. Access to this list requires email authorization, ensuring that only authorized users can retrieve the data.

    Returns:
        flask.Response: A JSON response containing an array of travel-related links.
    """
    return jsonify((Links.load_links_data()))

@bp.route('/api/links', methods=['POST'])
@require_email_authorization
def add_link():
    """
    Add a new link to the list of travel-related links.

    This endpoint accepts a JSON payload with the details of a new link and
    adds it to the existing list of links. Each new link is assigned a unique
    UUID and a position in the list. If notes are not provided in the payload,
    an empty string is assigned by default.

    Returns:
        flask.Response: A JSON response containing the details of the newly
        added link, with a 201 status code indicating successful creation.
    """
    data = request.get_json()
    if not data or not all([data.get('name'), data.get('url')]):
        abort(400, description="Missing required link data")

    # Call add_link without the position parameter
    new_link = Links.add_link(data['name'], data['url'], data.get('notes', ''))
    return jsonify(new_link.to_dict()), 201

@bp.route('/api/links/<id>', methods=['PUT'])
@require_email_authorization
def update_link(id):
    """
    Update an existing link's details.

    This endpoint allows for updating the details of an existing link identified
    by its ID. If the link with the given ID does not exist, it returns a 404
    error. Otherwise, it updates the link with the provided JSON payload,
    particularly the 'notes' field if specified.

    Args:
        id (str): The unique identifier of the link to be updated.

    Returns:
        flask.Response: A JSON response containing the updated link details, or
        a 404 error if the link with the given ID does not exist.
    """
    link = Links.get_by_id(id)
    if not link:
        abort(404, description="Link not found")

    data = request.get_json()
    try:
        link.update(**data)
        return jsonify(link.to_dict()), 200
    except Exception as e:
        # Assuming you have a way to handle rolling back within your model
        Links.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/links/<id>', methods=['DELETE'])
@require_email_authorization
def delete_link(id):
    """
    Delete a specific link from the list by its ID.

    This endpoint removes a link from the list of travel-related links using
    its unique identifier. If the operation is successful, it returns a 204
    No Content status, indicating that the item has been deleted.

    Args:
        id (str): The unique identifier of the link to be deleted.

    Returns:
        flask.Response: An empty response with a 204 status code indicating successful deletion.
    """
    if Links.delete_by_id(str(id)):
        return jsonify({'message': 'Link deleted successfully', 'id': str(id)}), 200
    else:
        abort(404, description="Link not found")

@bp.route('/clearall')
@require_email_authorization
def rebuild():
    Links.import_links_data()
    Visited.import_visited_data()
    return "Done"