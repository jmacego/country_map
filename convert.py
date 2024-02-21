import csv
import json

# Function to convert string to boolean
def str_to_bool(s):
    return s.lower() in ['true', '1', 't', 'y', 'yes']

# Path to your CSV file
csv_file_path = 'countries.csv'
# Path to the JSON file you want to create
json_file_path = 'visited.json'

# Read the CSV and convert it to a JSON format
data = []
with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for i, row in enumerate(csv_reader, 1):  # Start enumeration at 1 for the ID
        # Convert string booleans to actual booleans
        row['john'] = str_to_bool(row['john'])
        row['marcia'] = str_to_bool(row['marcia'])
        row['todo'] = str_to_bool(row['todo'])
        row['id'] = i  # Add an ID key with the enumeration value
        data.append(row)

# Write the data to a JSON file
with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
    json.dump(data, jsonfile, indent=4)
