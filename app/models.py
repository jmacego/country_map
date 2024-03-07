import json
import uuid

# File path for the visited data file
visited_file_path = 'instance/visited.json'

# File path for the links data file
links_file_path = 'instance/links.json'

class VisitedData:
    @staticmethod
    def load_visited_data():
        with open(visited_file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_visited_data(data):
        with open(visited_file_path, 'w') as file:
            json.dump(data, file, indent=4)

class LinksData:
    @staticmethod
    def load_links_data():
        with open(links_file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_links_data(data):
        with open(links_file_path, 'w') as file:
            json.dump(data, file, indent=4)