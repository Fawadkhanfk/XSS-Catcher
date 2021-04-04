import smtplib
import ssl
from email.mime.text import MIMEText
from typing import Any

import requests
from app.models import XSS, Settings
from flask import jsonify


def send_mail(recipient: str, xss: XSS = None) -> None:

    settings = Settings.query.first()

    if xss:
        msg = MIMEText(f"XSS Catcher just caught a new {xss.xss_type} XSS for client {xss.client_name}! Go check it out!")
        msg["Subject"] = f"Captured XSS for client {xss.client_name}"
    else:
        msg = MIMEText("This is a test email from XSS catcher. If you are getting this, it's because your SMTP configuration works. ")
        msg["Subject"] = "XSS Catcher mail test"

    msg["To"] = recipient
    msg["From"] = f"XSS Catcher <{settings.smtp_mail_from}>"

    if settings.smtp_ssl_tls:

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:

            smtp_server_login(settings, server)

            server.sendmail(settings.smtp_mail_from, recipient, msg.as_string())

    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:

            smtp_server_login(settings, server)

            if settings.starttls:
                server.starttls()

            server.sendmail(settings.smtp_mail_from, recipient, msg.as_string())


def send_webhook(recipient: str, xss: XSS = None) -> None:

    if xss:
        requests.post(url=recipient, json={"text": f"XSS Catcher just caught a new {xss.xss_type} XSS for client {xss.client.name}! Go check it out!"})

    else:
        requests.post(
            url=recipient, json={"text": "This is a test webhook from XSS catcher. If you are getting this, it's because your webhook configuration works."}
        )


def smtp_server_login(settings: Settings, server: smtplib.SMTP) -> None:
    if settings.smtp_user is not None and settings.smtp_password is not None:
        server.login(settings.smtp_user, settings.smtp_pass)


def generate_data_response(message: Any, status_code: int = 200) -> tuple:
    return jsonify(message), status_code


def generate_message_response(message: str, status_code: int = 200) -> tuple:
    return jsonify({"message": message}), status_code
