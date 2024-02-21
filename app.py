from flask import Flask, send_from_directory, jsonify, request
import geopandas as gpd
import pandas as pd
import numpy as np
import json
app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')
# File path for the visited data file
visited_file_path = 'visited.json'

# Function to load visited data from the file
def load_visited_data():
    with open(visited_file_path, 'r') as file:
        return json.load(file)

# Function to save visited data to the file
def save_visited_data(data):
    with open(visited_file_path, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/api/visited', methods=['GET'])
def get_visited():
    return jsonify(load_visited_data())

@app.route('/api/visited/<int:visited_id>', methods=['GET'])
def get_single_visited(visited_id):
    visited = load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == visited_id), None)
    return jsonify(visited_entry) if visited_entry else ('', 404)

@app.route('/api/visited', methods=['POST'])
def add_or_update_visited():
    visited = load_visited_data()
    new_visited = request.json
    # Find if the country already exists in the data
    existing_country = next((item for item in visited if item['name'].lower() == new_visited['name'].lower()), None)
    
    if existing_country:
        # Update existing country data
        existing_country.update(new_visited)
    else:
        # Assign a new ID and add the new country
        new_id = max(item['id'] for item in visited) + 1 if visited else 1
        new_visited['id'] = new_id
        visited.append(new_visited)
    
    save_visited_data(visited)
    return jsonify(new_visited), 200 if existing_country else 201

@app.route('/api/visited/<int:visited_id>', methods=['PUT'])
def update_visited(visited_id):
    visited = load_visited_data()
    visited_entry = next((item for item in visited if item['id'] == visited_id), None)
    if not visited_entry:
        return ('', 404)
    update_data = request.json
    visited_entry.update(update_data)
    save_visited_data(visited)
    return jsonify(visited_entry)

@app.route('/api/visited/<int:visited_id>', methods=['DELETE'])
def delete_visited(visited_id):
    visited = load_visited_data()
    visited = [item for item in visited if item['id'] != visited_id]
    save_visited_data(visited)
    return ('', 204)

@app.route('/api/geodata')
def geodata():
    gdf = gpd.read_file('country_data/ne_110m_admin_0_countries.shp')
    # Convert the GeoDataFrame to a GeoJSON
    countries_geojson = gdf.to_json()
    
    # jsonify takes care of the headers
    return jsonify(countries_geojson)

if __name__ == '__main__':
    app.run(debug=True)

