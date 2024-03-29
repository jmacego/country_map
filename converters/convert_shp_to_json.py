import geopandas as gpd
import json

def convert_shapefile_to_json(shapefile_path, output_json_path, name_field):
    # Read the shapefile using GeoPandas
    gdf = gpd.read_file(shapefile_path)

    # Rename the specified name field to 'name' for consistency
    gdf.rename(columns={name_field: 'name'}, inplace=True)

    # Select only the 'name' and 'geometry' columns
    gdf = gdf[['name', 'geometry']]

    # Convert the GeoDataFrame to a GeoJSON
    geojson_data = gdf.to_json()
    geojson_data = json.loads(geojson_data)

    # Save the GeoJSON data to a file
    with open(output_json_path, 'w') as file:
        json.dump(geojson_data, file, indent=4)

    print(f"Converted {shapefile_path} to {output_json_path}")

# Convert US states shapefile to JSON
convert_shapefile_to_json(
    shapefile_path='country_data/cb_2018_us_state_500k.shp',
    output_json_path='app/static/data/states.json',
    name_field='NAME'
)

