import json
import uuid

# Load the existing data from visited.json
with open('visited.json', 'r') as file:
    visited_data = json.load(file)

# Update each entry in the visited data
for entry in visited_data:
    # Replace the numeric ID with a UUID
    entry['id'] = str(uuid.uuid4())
    # Add the which_map field with a default value of 'world'
    entry['which_map'] = 'world'

# Save the updated data back to visited.json
with open('visited.json', 'w') as file:
    json.dump(visited_data, file, indent=4)

print("Updated visited.json with UUIDs and added which_map field.")
