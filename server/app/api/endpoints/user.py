import app.api.utils.validators.user.change_current_user_password as change_current_user_password_validators
from app import db
from app.api.endpoints import bp
from app.api.utils.shared import generate_data_response, generate_message_response, permissions
from app.api.utils.validators.shared import ValidationException
from app.models import User
from flask import jsonify, request
from flask_jwt_extended import get_current_user, jwt_required


@bp.route("/user", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def create_user():

    request_body = request.get_json()

    if "username" not in request_body.keys() or not request_body["username"]:

        return generate_message_response("Missing username", 400)

    if User.query.filter_by(username=request_body["username"]).first():
        return generate_message_response("This user already exists", 400)

    user = User(username=request_body["username"])

    password = user.generate_password()
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return generate_message_response(password)


@bp.route("/user/password", methods=["POST"])
@jwt_required()
def change_current_user_password():

    current_user = get_current_user()

    request_body = request.get_json()

    try:
        current_user.set_password(change_current_user_password_validators.validate_passwords(request_body, current_user))
    except ValidationException as error:
        return generate_message_response(str(error), 400)

    current_user.first_login = False

    db.session.commit()
    return jsonify({"status": "OK", "detail": "Password changed successfuly"}), 200


@bp.route("/user/<int:id>/password", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def reset_user_password(id):

    user = User.query.filter_by(id=id).first_or_404()

    password = user.generate_password()

    user.set_password(password)

    user.first_login = True

    db.session.commit()
    return generate_message_response(password)


@bp.route("/user/current", methods=["GET"])
@jwt_required()
def get_user():

    return generate_data_response(get_current_user().get_dict_representation())


@bp.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
@permissions(all_of=["admin"])
def delete_user(user_id):

    current_user = get_current_user()

    if len(User.query.all()) <= 1:
        return generate_message_response("Can't delete the only user", 400)

    if current_user.id == user_id:
        return generate_message_response("Can't delete yourself", 400)

    user = User.query.filter_by(id=user_id).first_or_404()

    db.session.delete(user)
    db.session.commit()

    return generate_message_response(f"User {user.username} deleted successfuly")


@bp.route("/user/<int:user_id>", methods=["PATCH"])
@jwt_required()
@permissions(all_of=["admin"])
def edit_user(user_id):

    if get_current_user().id == user_id:
        return generate_message_response("Can't demote yourself", 400)

    request_body = request.get_json()

    user = User.query.filter_by(id=user_id).first_or_404()

    if "is_admin" not in request_body.keys() or not request_body["is_admin"]:
        return generate_message_response("Missing data", 400)

    if not isinstance(request_body["is_admin"], bool):
        return generate_message_response("Invalid data", 400)

    user.is_admin = request_body["is_admin"]

    db.session.commit()
    return generate_message_response(f"User {user.username} modified successfuly")


@bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_list():

    users = []

    for user in User.query.all():
        users.append(user.get_dict_representation())

    return generate_data_response(users)
