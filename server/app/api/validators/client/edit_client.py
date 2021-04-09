from typing import Dict, Optional

from app.api.validators.shared import ValidationException, is_email, is_url
from app.models import Client, User


def validate_name(request_body: Dict, client: Client) -> str:

    if client.name != request_body["name"] and Client.query.filter_by(name=request_body["name"]).first():
        raise ValidationException("Another client already uses this name")

    return request_body["name"]


def validate_description(request_body: Dict) -> Optional[str]:

    return request_body["description"] if request_body["description"] else None


def validate_owner(request_body: Dict) -> int:

    if not User.query.filter_by(id=request_body["owner"]).first():
        raise ValidationException("This user does not exist")

    return request_body["owner"]


def validate_mail_to(request_body: Dict) -> Optional[str]:

    if not request_body["mail_to"]:
        return
    else:
        if not is_email(request_body["mail_to"]):
            raise ValidationException("Invalid mail recipient")

        return request_body["mail_to"]


def validate_webhook_url(request_body: Dict) -> Optional[str]:

    if not request_body["webhook_url"]:
        return
    else:
        if not is_url(request_body["webhook_url"]):
            raise ValidationException("Webhook URL format is invalid")

        return request_body["webhook_url"]
