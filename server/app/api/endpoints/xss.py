import json

from app import db
from app.api.endpoints import bp
from app.api.utils.shared import generate_data_response, generate_message_response, permissions
from app.api.utils.xss import (
    generate_captured_data_list,
    generate_get_xss_captured_data_filter_expression,
    generate_get_xss_list_filter_expression,
    generate_html_payload,
    generate_javascript_payload,
)
from app.api.validators.shared import ValidationException
from app.models import XSS, Client
from flask import request
from flask_jwt_extended import jwt_required


@bp.route("/xss/generate", methods=["POST"])
@jwt_required()
def generate_xss_payload():

    request_body = request.get_json()

    if "client_id" not in request_body.keys() or not request_body["client_id"]:
        return generate_message_response("Missing client ID", 400)

    if "url" not in request_body.keys() or not request_body["url"]:
        return generate_message_response("Missing URL", 400)

    if "xss_type" not in request_body.keys() or not request_body["xss_type"]:
        return generate_message_response("Missing XSS type", 400)

    if "code_type" not in request_body.keys() or not request_body["code_type"]:
        return generate_message_response("Missing code type", 400)

    if "data_to_gather" not in request_body.keys():
        return generate_message_response("Missing list of data to gather", 400)

    if "tags" not in request_body.keys():
        return generate_message_response("Missing tags", 400)

    client = Client.query.filter_by(id=request_body["client_id"]).first_or_404()

    if request_body["code_type"] == "html":
        payload = generate_html_payload(request_body["data_to_gather"], request_body["tags"], request_body["url"], request_body["xss_type"], client)

    else:
        payload = generate_javascript_payload(request_body["data_to_gather"], request_body["tags"], request_body["url"], request_body["xss_type"], client)

    return generate_message_response(payload)


@bp.route("/xss/<int:xss_id>", methods=["GET"])
@jwt_required()
def get_xss(xss_id):

    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    return generate_data_response(xss.get_dict_representation())


@bp.route("/xss/<int:xss_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def delete_xss(xss_id):

    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    db.session.delete(xss)
    db.session.commit()

    return generate_message_response("XSS deleted successfuly")


@bp.route("/xss/<int:xss_id>/data/<element_type>", methods=["GET"])
@jwt_required()
def get_xss_captured_data_element(xss_id, element_type):

    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    captured_data = json.loads(xss.data)

    return generate_data_response(captured_data[element_type])


@bp.route("/xss/<int:xss_id>/data/<element_type>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def delete_xss_captured_data_element(xss_id, element_type):

    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    captured_data = json.loads(xss.data)

    captured_data.pop(element_type, None)

    xss.data = json.dumps(captured_data)

    db.session.commit()

    return generate_message_response("Data deleted successfuly")


@bp.route("/xss", methods=["GET"])
@jwt_required()
def get_xss_list():

    query_parameters = request.args.to_dict()

    try:
        filter_expression = generate_get_xss_list_filter_expression(query_parameters)
    except ValidationException as error:
        return generate_message_response(str(error), 400)

    xss_list = []
    xss = XSS.query.filter_by(**filter_expression).all()

    for hit in xss:
        xss_list.append(hit.get_summary())

    return generate_data_response(xss_list)


@bp.route("/xss/data", methods=["GET"])
@jwt_required()
def get_xss_captured_data():

    query_parameters = request.args.to_dict()

    try:
        filter_expression = generate_get_xss_captured_data_filter_expression(query_parameters)
    except ValidationException as error:
        return generate_message_response(str(error), 400)

    xss_list = XSS.query.filter_by(**filter_expression).all()

    captured_data_list = generate_captured_data_list(xss_list)

    return generate_data_response(captured_data_list)
