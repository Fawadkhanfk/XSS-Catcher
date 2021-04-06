from flask import Blueprint

bp = Blueprint("api", __name__)

from app.api.endpoints import auth, client, settings, user, x, xss
