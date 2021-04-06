from app import db
from app.api.endpoints import bp
from app.api.utils.shared import generate_data_response, generate_message_response
from app.models import Blocklist, User
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_current_user, get_jwt, jwt_required


@bp.route("/auth/login", methods=["POST"])
@jwt_required(optional=True)
def login():

    if get_current_user():
        return generate_message_response("Already logged in", 400)

    request_body = request.get_json()

    if "username" not in request_body.keys() or "password" not in request_body.keys():
        return generate_message_response("Missing username or password", 400)

    user = User.query.filter_by(username=request_body["username"]).first()

    if not user or not user.check_password(request_body["password"]):
        return generate_message_response("Bad username or password", 403)

    return generate_data_response({"access_token": create_access_token(user.username), "refresh_token": create_refresh_token(user.username)})


@bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():

    return generate_data_response({"access_token": create_access_token(identity=get_current_user().username)})


@bp.route("/auth/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():

    blocked_jti = Blocklist(jti=get_jwt()["jti"])
    db.session.add(blocked_jti)
    db.session.commit()

    return generate_message_response("Logged out successfully")
