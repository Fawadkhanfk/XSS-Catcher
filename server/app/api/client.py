import app.api.validators.client.edit_client as edit_client_validator
from app import db
from app.api import bp
from app.api.validators.exceptions import ValidationException
from app.decorators import permissions
from app.models import XSS, Client
from app.utils import generate_data_response, generate_message_response
from flask import request
from flask_jwt_extended import get_current_user, jwt_required


@bp.route("/client", methods=["POST"])
@jwt_required()
def create_client():

    current_user = get_current_user()

    request_body = request.get_json()

    if "name" not in request_body.keys() or not request_body["name"]:
        return generate_message_response("Missing client name", 400)

    if "description" not in request_body.keys():
        return generate_message_response("Missing description", 400)

    if Client.query.filter_by(name=request_body["name"]).first():
        return generate_message_response("Client already exists", 400)

    new_client = Client(name=request_body["name"], description=request_body["description"] if request_body["description"] else None, owner_id=current_user.id)
    new_client.generate_uid()
    db.session.add(new_client)
    db.session.commit()

    return generate_message_response(f"New client {new_client.name} created successfuly", 201)


@bp.route("/client/<int:client_id>", methods=["GET"])
@jwt_required()
def get_client(client_id):

    client = Client.query.filter_by(id=client_id).first_or_404()

    return generate_data_response(client.get_dict_representation())


@bp.route("/client/<int:client_id>", methods=["PATCH"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def edit_client(client_id):

    request_body = request.get_json()

    client = Client.query.filter_by(id=client_id).first_or_404()

    try:
        if "name" in request_body.keys() and request_body["name"]:
            client.name = edit_client_validator.validate_name(request_body, client)

        if "description" in request_body.keys():
            client.description = edit_client_validator.validate_description(request_body)

        if "owner" in request_body.keys() and request_body["owner"] not in [None, ""]:
            client.owner_id = edit_client_validator.validate_owner(request_body)

        if "mail_to" in request_body.keys():
            client.mail_to = edit_client_validator.validate_mail_to(request_body)

        if "webhook_url" in request_body.keys():
            client.webhook_url = edit_client_validator.validate_webhook_url(request_body)

    except ValidationException as error:
        return generate_message_response(str(error), 400)

    db.session.commit()

    return generate_message_response(f"Client {client.name} edited successfuly")


@bp.route("/client/<int:client_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def delete_client(client_id):

    client = Client.query.filter_by(id=client_id).first_or_404()

    XSS.query.filter_by(client_id=client_id).delete()

    db.session.delete(client)
    db.session.commit()

    return generate_message_response(f"Client {client.name} deleted successfuly")


@bp.route("/client", methods=["GET"])
@jwt_required()
def get_client_list():

    client_list = []

    clients = Client.query.order_by(Client.id.desc()).all()

    for client in clients:
        client_list.append(client.get_dashboard_stats())

    return generate_data_response(client_list)
