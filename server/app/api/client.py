from app import db
from app.api import bp
from app.decorators import permissions
from app.models import XSS, Client, User
from app.utils import generate_data_response, generate_message_response
from app.validators import is_email, is_url
from flask import request
from flask_jwt_extended import get_current_user, jwt_required


@bp.route("/client", methods=["POST"])
@jwt_required()
def client__post():

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
def client_clientid__get(client_id):

    client = Client.query.filter_by(id=client_id).first_or_404()

    return generate_data_response(client.get_dict_representation())


@bp.route("/client/<int:client_id>", methods=["PATCH"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def client_clientid__patch(client_id):

    request_body = request.get_json()

    client = Client.query.filter_by(id=client_id).first_or_404()

    if "name" in request_body.keys() and request_body["name"]:

        if client.name != request_body["name"] and Client.query.filter_by(name=request_body["name"]).first():
            return generate_message_response("Another client already uses this name", 400)

        client.name = request_body["name"]

    if "description" in request_body.keys():

        client.description = request_body["description"] if request_body["description"] else None

    if "owner" in request_body.keys() and request_body["owner"] not in [None, ""]:

        if not User.query.filter_by(id=request_body["owner"]).first():
            return generate_message_response("This user does not exist", 400)

        client.owner_id = request_body["owner"]

    if "mail_to" in request_body.keys():

        if not request_body["mail_to"]:
            client.mail_to = None
        else:
            if not is_email(request_body["mail_to"]):
                return generate_message_response("Invalid mail recipient", 400)

            client.mail_to = request_body["mail_to"]

    if "webhook_url" in request_body.keys():

        if not request_body["webhook_url"]:
            client.webhook_url = None
        else:
            if not is_url(request_body["webhook_url"]):
                return generate_message_response("Webhook URL format is invalid", 400)

            client.webhook_url = request_body["webhook_url"]

    db.session.commit()

    return generate_message_response(f"Client {client.name} edited successfuly")


@bp.route("/client/<int:client_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def client_clientid__delete(client_id):

    client = Client.query.filter_by(id=client_id).first_or_404()

    XSS.query.filter_by(client_id=client_id).delete()

    db.session.delete(client)
    db.session.commit()

    return generate_message_response(f"Client {client.name} deleted successfuly")


@bp.route("/client", methods=["GET"])
@jwt_required()
def client__get():

    client_list = []

    clients = Client.query.order_by(Client.id.desc()).all()

    for client in clients:
        client_list.append(client.get_dashboard_stats())

    return generate_data_response(client_list)
