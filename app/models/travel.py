from flask import session, current_app, redirect, url_for
import json
import uuid
import os
from functools import wraps
from datetime import datetime, timedelta


# File path for the visited data file
visited_file_path = 'instance/visited.json'

# File path for the links data file
links_file_path = 'instance/links.json'

class VisitedData:
    """
    A class used to handle the loading and saving of visited data.

    This class provides static methods to load and save data related to visited places, such as countries or states, from a JSON file.
    """

    @staticmethod
    def load_visited_data():
        """
        Load visited data from a JSON file.

        This method reads from a file specified by 'visited_file_path' and loads the JSON data into memory.

        Returns:
            list: A list of dictionaries containing visited data.
        """
        with open(visited_file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_visited_data(data):
        """
        Save visited data to a JSON file.

        This method writes the provided data to a file specified by 'visited_file_path', formatting it with an indentation of 4 spaces for readability.

        Args:
            data (list): A list of dictionaries containing visited data to be saved.

        Returns:
            None
        """
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