from flask import Blueprint

sender_bp = Blueprint('sender', __name__, template_folder='templates')

from app.sender import routes
