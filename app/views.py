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

# Map Data
state_map_file = 'country_data/us_states.json'
country_map_file = 'country_data/countries.json'

# World Map
@views_blueprint.route('/')
@require_email_authorization
def country_map():
    with open(country_map_file, 'r') as file:
        geojson = json.load(file)
    return render_template('visited_map.html', title='Visited World', geojson=geojson)

# OAuth routes
@views_blueprint.route('/authorize/<provider>')
def oauth2_authorize(provider):

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

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('views.country_map'))

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
    return redirect(url_for('views.country_map'))

@views_blueprint.route('/email')
def email():
    return(session.get('email'))

# State Map
@views_blueprint.route('/states')
@require_email_authorization
def states():
    #gdf = gpd.read_file('country_data/tl_2023_us_state.shp')
    #gdf = gdf[['NAME', 'geometry']]
    #geojson = gdf.to_json()
    with open(state_map_file, 'r') as file:
        geojson = json.load(file)
    return render_template('visited_map.html', title='Visited States', geojson=geojson)

# Links
@views_blueprint.route('/links')
@require_email_authorization
def links():
    return render_template('links.html', title='Travel Links')

# Function to return a list of what areas have been visited
@views_blueprint.route('/api/visited', methods=['GET'])
@require_email_authorization
def get_visited():
    # Get the 'whichMap' query parameter from the URL
    which_map = request.args.get('whichMap', default='world', type=str).removeprefix('Visited ').lower()
    
    # Load the visited data from the file
    visited = visited = VisitedData.load_visited_data()
    
    # Filter the visited data based on the 'which_map' key
    filtered_visited = [place for place in visited if place.get('which_map') == which_map]
    
    return jsonify(filtered_visited)

@views_blueprint.route('/api/visited/<uuid:visited_id>', methods=['GET'])
@require_email_authorization
def get_single_visited(visited_id):
    visited = visited = VisitedData.load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    return jsonify(visited_entry) if visited_entry else ('', 404)

@views_blueprint.route('/api/visited', methods=['POST'])
@require_email_authorization
def add_or_update_visited():
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
    visited = visited = VisitedData.load_visited_data()
    visited = [item for item in visited if item['id'] != str(visited_id)]
    VisitedData.save_visited_data(visited)
    return ('', 204)

@views_blueprint.route('/api/links', methods=['GET'])
@require_email_authorization
def get_links():
    return jsonify(LinksData.load_links_data())

@views_blueprint.route('/api/links', methods=['POST'])
@require_email_authorization
def add_link():
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
    links = LinksData.load_links_data()
    links = [l for l in links if l['id'] != id]
    LinksData.save_links_data(links)
    return ('', 204)
