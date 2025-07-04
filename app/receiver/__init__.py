from flask import Blueprint

receiver_bp = Blueprint('receiver', __name__, template_folder='templates')

from app.receiver import routes
