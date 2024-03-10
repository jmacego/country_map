from flask import Flask, jsonify, render_template, request, Blueprint
import json
import uuid
from .models import VisitedData, LinksData

views_blueprint = Blueprint('views', __name__)

# Map Data
state_map_file = 'country_data/us_states.json'
country_map_file = 'country_data/countries.json'

# World Map
@views_blueprint.route('/')
def country_map():
    #gdf = gpd.read_file('country_data/ne_110m_admin_0_countries.shp')
    #gdf = gdf[['NAME_EN', 'geometry']]
    #geojson = gdf.to_json()
    with open(country_map_file, 'r') as file:
        geojson = json.load(file)
    return render_template('visited_map.html', title='Visited World', geojson=geojson)

# State Map
@views_blueprint.route('/states')
def states():
    #gdf = gpd.read_file('country_data/tl_2023_us_state.shp')
    #gdf = gdf[['NAME', 'geometry']]
    #geojson = gdf.to_json()
    with open(state_map_file, 'r') as file:
        geojson = json.load(file)
    return render_template('visited_map.html', title='Visited States', geojson=geojson)

# Links
@views_blueprint.route('/links')
def links():
    return render_template('links.html', title='Travel Links')

# Function to return a list of what areas have been visited
@views_blueprint.route('/api/visited', methods=['GET'])
def get_visited():
    # Get the 'whichMap' query parameter from the URL
    which_map = request.args.get('whichMap', default='world', type=str).removeprefix('Visited ').lower()
    
    # Load the visited data from the file
    visited = visited = VisitedData.load_visited_data()
    
    # Filter the visited data based on the 'which_map' key
    filtered_visited = [place for place in visited if place.get('which_map') == which_map]
    
    return jsonify(filtered_visited)

@views_blueprint.route('/api/visited/<uuid:visited_id>', methods=['GET'])
def get_single_visited(visited_id):
    visited = visited = VisitedData.load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    return jsonify(visited_entry) if visited_entry else ('', 404)

@views_blueprint.route('/api/visited', methods=['POST'])
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
def delete_visited(visited_id):
    visited = visited = VisitedData.load_visited_data()
    visited = [item for item in visited if item['id'] != str(visited_id)]
    VisitedData.save_visited_data(visited)
    return ('', 204)

@views_blueprint.route('/api/links', methods=['GET'])
def get_links():
    return jsonify(LinksData.load_links_data())

@views_blueprint.route('/api/links', methods=['POST'])
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
def delete_link(id):
    links = LinksData.load_links_data()
    links = [l for l in links if l['id'] != id]
    LinksData.save_links_data(links)
    return ('', 204)
