from flask import Blueprint

bp = Blueprint('travel', __name__, url_prefix='/travel')

from app.travel import routes