from app import db
from app.api import bp
from app.decorators import permissions
from app.models import XSS, Client, User
from app.utils import generate_data_response, generate_message_response
from app.validators import check_length, is_email, is_url
from flask import jsonify, request
from flask_jwt_extended import get_current_user, jwt_required


@bp.route("/client", methods=["POST"])
@jwt_required()
def client__post():

    current_user = get_current_user()

    request_body = request.get_json()

    if "name" not in request_body.keys() or not request_body["name"]:
        return generate_message_response("Missing client name", 400)

    if Client.query.filter_by(name=request_body["name"]).first():
        return generate_message_response("Client already exists", 400)

    client_description = request_body["description"] if "description" in request_body.keys() and request_body["description"] else None

    new_client = Client(name=request_body["name"], description=client_description, owner_id=current_user.id)
    new_client.gen_uid()
    db.session.add(new_client)
    db.session.commit()

    return generate_message_response(f"New client {new_client.name} created successfuly", 201)


@bp.route("/client/<int:client_id>", methods=["GET"])
@jwt_required()
def client_clientid__get(client_id):

    client = Client.query.filter_by(id=client_id).first_or_404()

    return generate_data_response(client.to_dict_client())


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

    ### YOU ARE HERE

    if "mail_to" in request_body.keys():

        if request_body["mail_to"] == "":
            client.mail_to = None
        else:
            if is_email(request_body["mail_to"]) and check_length(request_body["mail_to"], 256):
                client.mail_to = request_body["mail_to"]
            else:
                return jsonify({"status": "error", "detail": "Invalid mail recipient"}), 400
    else:
        client.mail_to = None

    if "webhook_url" in request_body.keys():
        if is_url(request_body["webhook_url"]):
            client.webhook_url = request_body["webhook_url"]
        else:
            return jsonify({"status": "error", "detail": "Webhook URL format is invalid"}), 400
    else:
        client.webhook_url = None

    db.session.commit()

    return jsonify({"status": "OK", "detail": "Client {} edited successfuly".format(client.name)}), 200


@bp.route("/client/<int:client_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def client_delete(client_id):
    """Deletes a client"""
    client = Client.query.filter_by(id=client_id).first_or_404()

    XSS.query.filter_by(client_id=client_id).delete()

    db.session.delete(client)
    db.session.commit()

    return jsonify({"status": "OK", "detail": "Client {} deleted successfuly".format(client.name)}), 200


@bp.route("/client", methods=["GET"])
@jwt_required()
def client_all_get():
    """Gets all clients"""
    client_list = []

    clients = Client.query.order_by(Client.id.desc()).all()

    for client in clients:
        client_list.append(client.to_dict_clients())

    return jsonify(client_list), 200
