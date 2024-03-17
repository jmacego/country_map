from flask import Blueprint

bp = Blueprint('finances', __name__, url_prefix='/finances')

from app.finances import routes