from app import db
from app.api import bp
from app.decorators import permissions
from app.models import Settings
from app.utils import generate_data_response, generate_message_response, send_mail, send_webhook
from app.validators import is_email, is_url
from flask import request
from flask_jwt_extended import jwt_required


@bp.route("/settings", methods=["GET"])
@jwt_required()
@permissions(all_of=["admin"])
def settings__get():

    settings = Settings.query.first()

    return generate_data_response(settings.get_dict_representation())


@bp.route("/settings", methods=["PATCH"])
@jwt_required()
@permissions(all_of=["admin"])
def settings__patch():

    request_body = request.get_json()

    settings = Settings.query.first()

    if "smtp_host" in request_body.keys():

        if not request_body["smtp_host"]:
            settings.smtp_host = None
        else:
            if "smtp_port" not in request_body.keys() or "smtp_mail_from" not in request_body.keys():
                return generate_message_response("Missing required SMTP setting(s)", 400)

            settings.smtp_host = request_body["smtp_host"]

    if "smtp_port" in request_body.keys():

        if request_body["smtp_port"] in ["", None]:
            settings.smtp_port = None
        else:
            if not isinstance(request_body["smtp_port"], int) or request_body["smtp_port"] > 65535 or request_body["smtp_port"] < 0:
                return generate_message_response("Port is invalid", 400)

            settings.smtp_port = request_body["smtp_port"]

    if "smtp_user" in request_body.keys():

        if not request_body["smtp_user"]:
            settings.smtp_user = None
        else:
            if "smtp_pass" not in request_body.keys():
                return generate_message_response("Missing SMTP password", 400)

            settings.smtp_user = request_body["smtp_user"]

    if "smtp_pass" in request_body.keys():

        if not request_body["smtp_pass"]:
            settings.smtp_pass = None
        else:
            if "smtp_user" not in request_body.keys():
                return generate_message_response("Missing SMTP username", 400)

            settings.smtp_pass = request_body["smtp_pass"]

    if "smtp_mail_from" in request_body.keys():

        if not request_body["smtp_mail_from"]:
            settings.smtp_mail_from = None
        else:
            if not is_email(request_body["smtp_mail_from"]):
                return generate_message_response("Sender email address format is invalid", 400)

            settings.smtp_mail_from = request_body["smtp_mail_from"]

    if "smtp_mail_to" in request_body.keys():

        if not request_body["smtp_mail_to"]:
            settings.smtp_mail_to = None
        else:
            if not is_email(request_body["smtp_mail_to"]):
                return generate_message_response("Recipient email address format is invalid", 400)

            settings.smtp_mail_to = request_body["smtp_mail_to"]

    if "smtp_ssl_tls" in request_body.keys():

        if not request_body["smtp_ssl_tls"]:
            settings.smtp_ssl_tls = False
        else:
            if not isinstance(request_body["smtp_ssl_tls"], bool):
                return generate_message_response("smtp_ssl_tls parameter must be true or false", 400)

            if "smtp_starttls" in request_body.keys():
                return generate_message_response("Cannot use SSL/TLS and STARTTLS at the same time", 400)

            settings.smtp_ssl_tls = request_body["smtp_ssl_tls"]

    if "smtp_starttls" in request_body.keys():

        if not request_body["smtp_starttls"]:
            settings.smtp_starttls = False
        else:
            if not isinstance(request_body["smtp_starttls"], bool):
                return generate_message_response("smtp_starttls parameter must be true or false", 400)

            settings.smtp_starttls = request_body["smtp_starttls"]

    if "webhook_url" in request_body.keys():

        if not request_body["webhook_url"]:
            settings.webhook_url = None
        else:
            if not is_url(request_body["webhook_url"]):
                return generate_message_response("Webhook URL format is invalid", 400)

            settings.webhook_url = request_body["webhook_url"]

    db.session.commit()

    return generate_message_response("Configuration saved successfuly")


@bp.route("/settings/test/smtp", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def settings_test_smtp__post():

    request_body = request.get_json()

    if "mail_to" not in request_body.keys() or not request_body["mail_to"]:
        return generate_message_response("Missing recipient", 400)

    if not is_email(request_body["mail_to"]):
        return generate_message_response("Invalid recipient", 400)

    try:
        send_mail(receiver=request_body["mail_to"])
        return generate_message_response("SMTP configuration test successful")
    except:
        return generate_message_response("Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it.", 400)


@bp.route("/settings/test/webhook", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def settings_test_webhook__post():

    request_body = request.get_json()

    if "url" not in request_body.keys() or not request_body["url"]:
        return generate_message_response("Missing URL", 400)

    if not is_url(request_body["url"]):
        return generate_message_response("Invalid URL", 400)

    try:
        send_webhook(receiver=request_body["url"])
        return generate_message_response("Webhook configuration test successful")
    except:
        return generate_message_response("Could not send test webhook", 400)
