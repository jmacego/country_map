import json
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from app.extensions import db

# File path for the visited data file
visited_file_path = 'instance/visited.json'

# File path for the links data file
links_file_path = 'instance/links.json'


class Visited(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    john = db.Column(db.Boolean, default=False)
    marcia = db.Column(db.Boolean, default=False)
    todo = db.Column(db.Boolean, default=False)
    which_map = db.Column(db.String(50))

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    @staticmethod
    def load_visited_data():
        return [visited.to_dict() for visited in Visited.query.all()]

    @classmethod
    def update_entry(cls, id, data):
        visited_entry = cls.query.get(id)
        if visited_entry:
            for key, value in data.items():
                if hasattr(visited_entry, key):
                    setattr(visited_entry, key, value)
            db.session.commit()
            return visited_entry
        return None
    
    @classmethod
    def delete_by_id(cls, id):
        visited_entry = cls.query.get(id)
        if visited_entry:
            db.session.delete(visited_entry)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def save_visited_data(name, john, marcia, todo, which_map):
        visited = Visited(name=name, john=john, marcia=marcia, todo=todo, which_map=which_map)
        db.session.add(visited)
        db.session.commit()

    @classmethod
    def add_new_entry(cls, name, john, marcia, todo, which_map):
        new_visited = cls(
            id=str(uuid.uuid4()),  # Generate a unique UUID for the new entry
            name=name,
            john=john,
            marcia=marcia,
            todo=todo,
            which_map=which_map
        )
        db.session.add(new_visited)
        db.session.commit()
        return new_visited
    
    @classmethod
    def import_visited_data(cls):
        with open('instance/visited.json', 'r') as file:
            visited_data = json.load(file)
            for item in visited_data:
                visited = cls(
                    name=item['name'],
                    id=item['id'],
                    john=item['john'],
                    marcia=item['marcia'],
                    todo=item['todo'],
                    which_map=item['which_map']
                )
                db.session.add(visited)
            db.session.commit()

class Links(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    @staticmethod
    def load_links_data():
        return [link.to_dict() for link in Links.query.all()]

    @staticmethod
    def save_links_data(name, url, notes, position):
        link = Links(name=name, url=url, notes=notes, position=position)
        db.session.add(link)
        db.session.commit()

    @staticmethod
    def add_link(name, url, notes):
        # Find the highest position value in the database
        max_position = db.session.query(func.max(Links.position)).scalar() or 0
        # Calculate the next position
        next_position = max_position + 1

        # Create a new link with the next position
        link = Links(
            id=str(uuid.uuid4()),  # Generate a unique UUID for the new link
            name=name,
            url=url,
            notes=notes,
            position=next_position
        )
        db.session.add(link)
        db.session.commit()
        return link

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def delete_by_id(cls, id):
        link_to_delete = cls.query.get(id)
        if link_to_delete:
            db.session.delete(link_to_delete)
            db.session.commit()
            return True
        return False

    @classmethod
    def import_links_data(cls):
        db.drop_all()
        db.create_all()
        with open('instance/links.json', 'r') as file:
            links_data = json.load(file)
            for item in links_data:
                link = cls(
                    id=item['id'],
                    name=item['name'],
                    url=item['url'],
                    notes=item['notes'],
                    position=item['position']
                )
                db.session.add(link)
            db.session.commit()
