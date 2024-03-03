from flask import Flask, send_from_directory, jsonify, request, render_template
import geopandas as gpd
import pandas as pd
import numpy as np
import json
import uuid
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# File path for the visited data file
visited_file_path = 'visited.json'

# File path for the links data file
links_file_path = 'links.json'

# Map Data
state_map_file = 'country_data/us_states.json'
country_map_file = 'country_data/countries.json'

# World Map
@app.route('/')
def country_map():
    #gdf = gpd.read_file('country_data/ne_110m_admin_0_countries.shp')
    #gdf = gdf[['NAME_EN', 'geometry']]
    #geojson = gdf.to_json()
    with open(country_map_file, 'r') as file:
        geojson = json.load(file)
    return render_template('visited_map.html', title='Visited World', geojson=geojson)

# State Map
@app.route('/states')
def states():
    #gdf = gpd.read_file('country_data/tl_2023_us_state.shp')
    #gdf = gdf[['NAME', 'geometry']]
    #geojson = gdf.to_json()
    with open(state_map_file, 'r') as file:
        geojson = json.load(file)
    return render_template('visited_map.html', title='Visited States', geojson=geojson)

# Links
@app.route('/links')
def links():
    return render_template('links.html', title='Travel Links')

# Function to load visited data from the file
def load_visited_data():
    with open(visited_file_path, 'r') as file:
        return json.load(file)

# Function to save visited data to the file
def save_visited_data(data):
    with open(visited_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to load links data from the file
def load_links_data():
    with open(links_file_path, 'r') as file:
        return json.load(file)

# Function to save links data to the file
def save_links_data(data):
    with open(links_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to return a list of what areas have been visited
@app.route('/api/visited', methods=['GET'])
def get_visited():
    # Get the 'whichMap' query parameter from the URL
    which_map = request.args.get('whichMap', default='world', type=str).removeprefix('Visited ').lower()
    
    # Load the visited data from the file
    visited = load_visited_data()
    
    # Filter the visited data based on the 'which_map' key
    filtered_visited = [place for place in visited if place.get('which_map') == which_map]
    
    return jsonify(filtered_visited)

@app.route('/api/visited/<uuid:visited_id>', methods=['GET'])
def get_single_visited(visited_id):
    visited = load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    return jsonify(visited_entry) if visited_entry else ('', 404)

@app.route('/api/visited', methods=['POST'])
def add_or_update_visited():
    # Get the 'whichMap' query parameter from the URL
    visited = load_visited_data()
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
    
    save_visited_data(visited)
    return jsonify(new_visited), 200 if existing_country else 201

@app.route('/api/visited/<uuid:visited_id>', methods=['PUT'])
def update_visited(visited_id):
    visited = load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == str(visited_id)), None)
    if not visited_entry:
        return ('', 404)
    update_data = request.json
    visited_entry.update(update_data)
    save_visited_data(visited)
    return jsonify(visited_entry)

@app.route('/api/visited/<uuid:visited_id>', methods=['DELETE'])
def delete_visited(visited_id):
    visited = load_visited_data()
    visited = [item for item in visited if item['id'] != str(visited_id)]
    save_visited_data(visited)
    return ('', 204)

@app.route('/api/links', methods=['GET'])
def get_links():
    return jsonify(load_links_data())

@app.route('/api/links', methods=['POST'])
def add_link():
    links = load_links_data()
    new_link = request.json
    new_link['id'] = str(uuid.uuid4())  # Generate a unique ID
    new_link['position'] = len(links) + 1  # Assign position
    new_link['notes'] = new_link.get('notes', '')  # Add notes field
    links.append(new_link)
    save_links_data(links)
    return jsonify(new_link), 201

@app.route('/api/links/<id>', methods=['PUT'])
def update_link(id):
    links = load_links_data()
    link = next((l for l in links if l['id'] == id), None)
    if not link:
        return ('', 404)
    update_data = request.json
    link['notes'] = update_data.get('notes', link.get('notes', ''))  # Update notes field
    link.update(update_data)
    save_links_data(links)
    return jsonify(link)

@app.route('/api/links/<id>', methods=['DELETE'])
def delete_link(id):
    links = load_links_data()
    links = [l for l in links if l['id'] != id]
    save_links_data(links)
    return ('', 204)


if __name__ == '__main__':
    app.run(debug=True)

