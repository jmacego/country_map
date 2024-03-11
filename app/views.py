from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for, session, make_response, session, current_app
from requests_oauthlib import OAuth2Session
import json
import uuid
import os
import secrets
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode
from .models import VisitedData, LinksData, require_email_authorization

# Load environment variables
load_dotenv()
views_blueprint = Blueprint('views', __name__)

@views_blueprint.route('/')
@require_email_authorization
def world_map():
    """
    Display a world map with visited countries.

    This route handles the main page view of the application, where a world map highlighting visited countries is displayed. It requires email authorization before access is granted.

    Returns:
        render_template (flask.Response): A Flask response object that renders the 'visited_map.html' template with the title 'Visited World'.
    """
    return render_template('visited_map.html', title='Visited World')

@views_blueprint.route('/states')
@require_email_authorization
def states():
    """
    Display a US map with visited states.

    This route serves the page that shows a map of the United States, highlighting the states that have been visited. Access to this page is restricted and requires email authorization before viewing.

    Returns:
        render_template (flask.Response): A Flask response object that renders the 'visited_map.html' template with the title 'Visited States'.
    """
    return render_template('visited_map.html', title='Visited States')

@views_blueprint.route('/links')
@require_email_authorization
def links():
    """
    Display and modify a list of useful travel-related links.

    This route provides an interface for displaying and potentially modifying a curated list of travel-related links. It requires email authorization for access, ensuring that only authorized users can view or modify the links.

    Returns:
        render_template (flask.Response): A Flask response object that renders the 'links.html' template with the title 'Travel Links'.
    """
    return render_template('links.html', title='Travel Links')


@views_blueprint.route('/api/visited', methods=['GET'])
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


@views_blueprint.route('/api/visited/<uuid:visited_id>', methods=['GET'])
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


@views_blueprint.route('/api/visited', methods=['POST'])
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

@views_blueprint.route('/api/visited/<uuid:visited_id>', methods=['PUT'])
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

@views_blueprint.route('/api/visited/<uuid:visited_id>', methods=['DELETE'])
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

@views_blueprint.route('/api/links', methods=['GET'])
@require_email_authorization
def get_links():
    """
    Retrieve a list of useful travel-related links.

    This endpoint fetches a list of travel-related links that may be useful for users. Access to this list requires email authorization, ensuring that only authorized users can retrieve the data.

    Returns:
        flask.Response: A JSON response containing an array of travel-related links.
    """
    return jsonify(LinksData.load_links_data())

@views_blueprint.route('/api/links', methods=['POST'])
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

@views_blueprint.route('/api/links/<id>', methods=['PUT'])
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

@views_blueprint.route('/api/links/<id>', methods=['DELETE'])
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

@views_blueprint.route('/authorize/<provider>')
def oauth2_authorize(provider):
    """
    Initiate OAuth2 authorization for a specified provider.

    This endpoint initiates the OAuth2 authorization process for a given provider. It generates a state token for security, constructs a query string with OAuth2 parameters, and redirects the user to the provider's authorization URL.

    Args:
        provider (str): The name of the OAuth2 provider to authorize.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the OAuth2 provider's authorization URL with the necessary query parameters.

    Raises:
        HTTPException: An HTTP 404 error if the provider is not configured.
    """
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('views.oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + qs)

@views_blueprint.route('/callback/<provider>')
def oauth2_callback(provider):
    """
    Handle the OAuth2 callback from the provider.

    This endpoint processes the callback after a user has authenticated with an OAuth2 provider. It validates the state parameter, exchanges the authorization code for an access token, and retrieves the user's email address using the access token. If any step fails, it aborts the process with the appropriate error code.

    Args:
        provider (str): The name of the OAuth2 provider.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the 'world_map' view if successful, or an error response if any step of the authentication process fails.

    Raises:
        HTTPException: An HTTP 404 error if the provider is not configured, a 401 error if there is an authentication error, or if the state parameter or authorization code is invalid.
    """
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('views.world_map'))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('views.oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    session['email'] = email
    return redirect(url_for('views.world_map'))

@views_blueprint.route('/email')
def email():
    """Test route. Display e-mail user is logged in as"""
    return(session.get('email'))
