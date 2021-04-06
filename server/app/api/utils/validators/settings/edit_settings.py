from typing import Optional

from app.api.utils.validators.shared import ValidationException, is_email, is_url


def validate_smtp_host(request_body: dict) -> Optional[str]:

    if not request_body["smtp_host"]:
        return
    else:
        if "smtp_port" not in request_body.keys() or "smtp_mail_from" not in request_body.keys():
            raise ValidationException("Missing required SMTP setting(s)")

        return request_body["smtp_host"]


def validate_smtp_port(request_body: dict) -> Optional[int]:

    if request_body["smtp_port"] in ["", None]:
        return
    else:
        if not isinstance(request_body["smtp_port"], int) or request_body["smtp_port"] > 65535 or request_body["smtp_port"] < 0:
            raise ValidationException("Port is invalid")

        return request_body["smtp_port"]


def validate_smtp_user(request_body: dict) -> Optional[str]:

    if not request_body["smtp_user"]:
        return
    else:
        if "smtp_pass" not in request_body.keys():
            raise ValidationException("Missing SMTP password")

        return request_body["smtp_user"]


def validate_smtp_pass(request_body: dict) -> Optional[str]:

    if not request_body["smtp_pass"]:
        return
    else:
        if "smtp_user" not in request_body.keys():
            raise ValidationException("Missing SMTP username")

        return request_body["smtp_pass"]


def validate_mail_from(request_body: dict) -> Optional[str]:

    if not request_body["smtp_mail_from"]:
        return
    else:
        if not is_email(request_body["smtp_mail_from"]):
            raise ValidationException("Sender email address format is invalid")

        return request_body["smtp_mail_from"]


def validate_mail_to(request_body: dict) -> Optional[str]:

    if not request_body["smtp_mail_to"]:
        return
    else:
        if not is_email(request_body["smtp_mail_to"]):
            raise ValidationException("Recipient email address format is invalid")

        return request_body["smtp_mail_to"]


def validate_smtp_ssl_tls(request_body: dict) -> Optional[bool]:

    if not request_body["smtp_ssl_tls"]:
        return False
    else:
        if not isinstance(request_body["smtp_ssl_tls"], bool):
            raise ValidationException("smtp_ssl_tls parameter must be true or false")

        if "smtp_starttls" in request_body.keys():
            raise ValidationException("Cannot use SSL/TLS and STARTTLS at the same time")

        return request_body["smtp_ssl_tls"]


def validate_smtp_starttls(request_body: dict) -> Optional[bool]:

    if not request_body["smtp_starttls"]:
        return False
    else:
        if not isinstance(request_body["smtp_starttls"], bool):
            raise ValidationException("smtp_starttls parameter must be true or false")

        if "smtp_ssl_tls" in request_body.keys():
            raise ValidationException("Cannot use SSL/TLS and STARTTLS at the same time")

        return request_body["smtp_starttls"]


def validate_webhook_url(request_body: dict) -> Optional[str]:

    if not request_body["webhook_url"]:
        return
    else:
        if not is_url(request_body["webhook_url"]):
            raise ValidationException("Webhook URL format is invalid")

        return request_body["webhook_url"]
