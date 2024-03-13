from flask import Blueprint

bp = Blueprint('dates', __name__, url_prefix='/dates')

from app.dates import routes