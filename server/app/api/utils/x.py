import json
import time
from typing import Dict, List, Tuple

from app.api.utils.shared import send_mail, send_webhook
from app.models import XSS, Client, Settings
from werkzeug.local import LocalProxy


def generate_xss_properties(request: LocalProxy, xss_type: str, client: Client) -> Dict:

    xss_data, tags = parse_parameters(request)

    return {
        "headers": json.dumps({header_name: header_value for header_name, header_value in request.headers.items()}),
        "ip_addr": request.headers["X-Forwarded-For"].split(", ")[0] if "X-Forwarded-For" in request.headers else request.remote_addr,
        "client_id": client.id,
        "xss_type": "stored" if xss_type == "s" else "reflected",
        "data": json.dumps(xss_data),
        "timestamp": int(time.time()),
        "tags": json.dumps(tags),
    }


def parse_parameters(request: LocalProxy) -> Tuple[Dict, List[str]]:

    xss_data = {}
    tags = []

    for parameter_name, parameter_value in extract_parameters_from_request(request).items():

        if parameter_name == "cookies":
            if "cookies" not in xss_data.keys():
                xss_data["cookies"] = {}
            xss_data["cookies"].update(parse_cookies(parameter_value))

        elif parameter_name == "local_storage":
            if "local_storage" not in xss_data.keys():
                xss_data["local_storage"] = {}
            xss_data["local_storage"].update(parse_storage(parameter_value))

        elif parameter_name == "session_storage":
            if "session_storage" not in xss_data.keys():
                xss_data["session_storage"] = {}
            xss_data["session_storage"].update(parse_storage(parameter_value))

        elif parameter_name == "dom":
            xss_data["dom"] = f"<html>\n{parameter_value}\n</html>"

        elif parameter_name == "tags":
            tags = parameter_value.split(",")

        else:
            xss_data[parameter_name] = parameter_value

    return xss_data, tags


def extract_parameters_from_request(request: LocalProxy) -> Dict:

    if request.method == "GET":
        parameters = request.args.to_dict()
    elif request.method == "POST":
        if request.is_json:
            parameters = request.get_json()
        else:
            parameters = request.form

    return parameters


def parse_cookies(cookies_raw: str) -> Dict:

    cookies = {}

    cookie_list = cookies_raw.split("; ")
    for cookie in cookie_list:
        cookie_splitted = cookie.split("=")
        cookie_name = cookie_splitted[0]
        cookie_value = "".join(cookie_splitted[1:])
        cookies.update({cookie_name: cookie_value})

    return cookies


def parse_storage(storage_raw: str) -> Dict:

    storage = {}

    storage_dict = json.loads(storage_raw)
    for element_name, element_value in storage_dict.items():
        storage.update({element_name: element_value})

    return storage


def send_alert(xss: XSS) -> None:

    settings = Settings.query.first()

    if (xss.client.mail_to or settings.smtp_mail_to) and settings.smtp_host:

        mail_recipient = xss.client.mail_to if xss.client.mail_to else settings.smtp_mail_to

        try:
            send_mail(mail_recipient, xss)
        except:
            pass

    if xss.client.webhook_url or settings.webhook_url:

        webhook_recipient = xss.client.webhook_url if xss.client.webhook_url else settings.webhook_url

        try:
            send_webhook(webhook_recipient, xss)
        except:
            pass
