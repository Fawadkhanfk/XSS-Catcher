import app.api.validators.settings.edit_settings as edit_settings_validators
from app import db
from app.api import bp
from app.api.validators.exceptions import ValidationException
from app.decorators import permissions
from app.models import Settings
from app.utils import generate_data_response, generate_message_response, send_mail, send_webhook
from app.validators import is_email, is_url
from flask import request
from flask_jwt_extended import jwt_required


@bp.route("/settings", methods=["GET"])
@jwt_required()
@permissions(all_of=["admin"])
def get_settings():

    settings = Settings.query.first()

    return generate_data_response(settings.get_dict_representation())


@bp.route("/settings", methods=["PATCH"])
@jwt_required()
@permissions(all_of=["admin"])
def edit_settings():

    request_body = request.get_json()

    settings = Settings.query.first()

    try:
        if "smtp_host" in request_body:
            settings.smtp_host = edit_settings_validators.validate_smtp_host(request_body)

        if "smtp_port" in request_body:
            settings.smtp_port = edit_settings_validators.validate_smtp_port(request_body)

        if "smtp_user" in request_body:
            settings.smtp_user = edit_settings_validators.validate_smtp_user(request_body)

        if "smtp_pass" in request_body:
            settings.smtp_pass = edit_settings_validators.validate_smtp_pass(request_body)

        if "smtp_mail_from" in request_body:
            settings.smtp_mail_from = edit_settings_validators.validate_mail_from(request_body)

        if "smtp_mail_to" in request_body:
            settings.smtp_mail_to = edit_settings_validators.validate_mail_to(request_body)

        if "smtp_ssl_tls" in request_body:
            settings.smtp_ssl_tls = edit_settings_validators.validate_smtp_ssl_tls(request_body)

        if "smtp_starttls" in request_body:
            settings.smtp_starttls = edit_settings_validators.validate_smtp_starttls(request_body)

        if "webhook_url" in request_body:
            settings.webhook_url = edit_settings_validators.validate_webhook_url(request_body)

    except ValidationException as error:
        return generate_message_response(str(error), 400)

    db.session.commit()

    return generate_message_response("Configuration saved successfuly")


@bp.route("/settings/test/smtp", methods=["POST"])
@jwt_required()
@permissions(all_of=["admin"])
def test_smtp_settings():

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
def test_webhook_settings():

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
