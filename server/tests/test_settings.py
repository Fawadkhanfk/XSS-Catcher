import json

import pytest
from app.api.utils.shared import send_mail
from app.models import Settings

from .fixtures import client
from .functions import *

# Tests


def test_patch_settings(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    patch_settings(
        client,
        access_header,
        smtp_host="127.0.0.1",
        smtp_port=465,
        smtp_ssl_tls=True,
        smtp_mail_from="xsscatcher@hackerman.ca",
        smtp_user="admin",
        smtp_pass="admin",
        smtp_mail_to="dax@hackerman.ca",
    )
    settings = Settings.query.first()
    assert settings.smtp_host == "127.0.0.1"
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port="a", smtp_mail_from="xsscatcher@hackerman.ca")
    assert b"Port is invalid" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=65536, smtp_mail_from="xsscatcher@hackerman.ca")
    assert b"Port is invalid" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1")
    assert b"Missing required SMTP setting(s)" in rv.data
    rv = patch_settings(
        client, access_header, smtp_host="127.0.0.1", smtp_port=465, smtp_starttls=True, smtp_ssl_tls=True, smtp_mail_from="xsscatcher@hackerman.ca"
    )
    assert b"Cannot use SSL/TLS and STARTTLS at the same time" in rv.data
    rv = patch_settings(
        client, access_header, smtp_host="127.0.0.1", smtp_port=587, smtp_starttls=True, smtp_mail_from="xsscatcher@hackerman.ca", smtp_mail_to="test"
    )
    assert b"Recipient email address format is invalid" in rv.data
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=587, smtp_starttls=True, smtp_mail_from="xsscatcher@hackerman.ca")
    settings = Settings.query.first()
    assert settings.smtp_starttls == True
    patch_settings(
        client, access_header, smtp_host="127.0.0.1", smtp_port=25, smtp_mail_from="xsscatcher@hackerman.ca", smtp_starttls=False, smtp_ssl_tls=False
    )
    settings = Settings.query.first()
    assert settings.smtp_starttls == False and settings.smtp_ssl_tls == False
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, smtp_mail_from="test")
    assert b"Sender email address format is invalid" in rv.data
    rv = patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25)
    assert b"Missing required SMTP setting(s)" in rv.data
    rv = patch_settings(client, access_header, webhook_url="abc")
    assert b"Webhook URL format is invalid" in rv.data
    patch_settings(client, access_header, webhook_url="http://localhost/test")
    settings = Settings.query.first()
    assert settings.webhook_url == "http://localhost/test"


def test_get_settings(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = get_settings(client, access_header)
    assert json.loads(rv.data)["smtp_host"] == None


def test_send_mail(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=25, smtp_mail_from="xsscatcher@hackerman.ca")
    rv = send_test_mail(client, access_header)
    assert b"Missing recipient" in rv.data
    rv = send_test_mail(client, access_header, mail_to="test")
    assert b"Invalid recipient" in rv.data
    rv = send_test_mail(client, access_header, mail_to="dax@hackerman.ca")
    assert b"Could not send test email" in rv.data
    patch_settings(client, access_header, smtp_host="127.0.0.1", smtp_port=587, smtp_ssl_tls=True, smtp_mail_from="xsscatcher@hackerman.ca")
    rv = send_test_mail(client, access_header, mail_to="dax@hackerman.ca")
    assert b"Could not send test email" in rv.data


def test_send_webook(client):
    access_header, _ = login_get_headers(client, "admin", "xss")
    rv = send_test_webhook(client, access_header)
    assert b"Missing URL" in rv.data
    rv = send_test_webhook(client, access_header, url="http://localhost:54321")
    assert b"Could not send test webhook" in rv.data
