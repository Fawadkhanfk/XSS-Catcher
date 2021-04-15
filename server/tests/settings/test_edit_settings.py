from unittest import mock

ENDPOINT = "/api/settings"


def test__edit_settings__valid_data_ssl_tls__200(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={
            "smtp_host": "smtp.hackerman.ca",
            "smtp_port": 465,
            "smtp_user": "test",
            "smtp_pass": "test",
            "smtp_mail_from": "xss-catcher@hackerman.ca",
            "smtp_mail_to": "dax@hackerman.ca",
            "smtp_ssl_tls": True,
            "webhook_url": "https://hackerman.ca",
        },
    )

    assert response.status_code == 200
    assert response.json["message"] == "Configuration saved successfuly"


def test__edit_settings__valid_data_starttls__200(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={
            "smtp_host": "smtp.hackerman.ca",
            "smtp_port": 587,
            "smtp_user": "test",
            "smtp_pass": "test",
            "smtp_mail_from": "xss-catcher@hackerman.ca",
            "smtp_mail_to": "dax@hackerman.ca",
            "smtp_starttls": True,
            "webhook_url": "https://hackerman.ca",
        },
    )

    assert response.status_code == 200
    assert response.json["message"] == "Configuration saved successfuly"


def test__edit_settings__missing_smtp_data__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(ENDPOINT, headers=authorization_headers["access_header"], json={"smtp_host": "smtp.hackerman.ca"})

    assert response.status_code == 400
    assert response.json["message"] == "Missing required SMTP setting(s)"


def test__edit_settings__invalid_port__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"smtp_host": "smtp.hackerman.ca", "smtp_port": 70000, "smtp_mail_from": "xss-catcher@hackerman.ca"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Port is invalid"


def test__edit_settings__missing_smtp_password__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={
            "smtp_host": "smtp.hackerman.ca",
            "smtp_port": 25,
            "smtp_user": "test",
            "smtp_mail_from": "xss-catcher@hackerman.ca",
        },
    )

    assert response.status_code == 400
    assert response.json["message"] == "Missing SMTP password"


def test__edit_settings__missing_smtp_username__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={
            "smtp_host": "smtp.hackerman.ca",
            "smtp_port": 25,
            "smtp_pass": "test",
            "smtp_mail_from": "xss-catcher@hackerman.ca",
        },
    )

    assert response.status_code == 400
    assert response.json["message"] == "Missing SMTP username"


def test__edit_settings__invalid_smtp_mail_from__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={
            "smtp_host": "smtp.hackerman.ca",
            "smtp_port": 25,
            "smtp_mail_from": "test",
        },
    )

    assert response.status_code == 400
    assert response.json["message"] == "Sender email address format is invalid"


def test__edit_settings__invalid_smtp_mail_to__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"smtp_host": "smtp.hackerman.ca", "smtp_port": 25, "smtp_mail_from": "xss-catcher@hackerman.ca", "smtp_mail_to": "test"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Recipient email address format is invalid"


def test__edit_settings__invalid_ssl_tls__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"smtp_host": "smtp.hackerman.ca", "smtp_port": 465, "smtp_mail_from": "xss-catcher@hackerman.ca", "smtp_ssl_tls": "test"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "smtp_ssl_tls parameter must be true or false"


def test__edit_settings__invalid_starttls__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"smtp_host": "smtp.hackerman.ca", "smtp_port": 587, "smtp_mail_from": "xss-catcher@hackerman.ca", "smtp_starttls": "test"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "smtp_starttls parameter must be true or false"


def test__edit_settings__both_ssl_and_starttls__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"smtp_host": "smtp.hackerman.ca", "smtp_port": 465, "smtp_mail_from": "xss-catcher@hackerman.ca", "smtp_ssl_tls": True, "smtp_starttls": True},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Cannot use SSL/TLS and STARTTLS at the same time"


@mock.patch("app.api.validators.settings.edit_settings.validate_smtp_ssl_tls")
def test__edit_settings__both_starttls_and_ssl__400(validate_smtp_ssl_tls_mocker, test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"smtp_host": "smtp.hackerman.ca", "smtp_port": 465, "smtp_mail_from": "xss-catcher@hackerman.ca", "smtp_ssl_tls": True, "smtp_starttls": True},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Cannot use SSL/TLS and STARTTLS at the same time"


def test__edit_settings__invalid_webhook_url__400(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={"webhook_url": "test"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Webhook URL format is invalid"


def test__edit_settings__unset_values__200(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT,
        headers=authorization_headers["access_header"],
        json={
            "smtp_host": None,
            "smtp_port": None,
            "smtp_user": None,
            "smtp_pass": None,
            "smtp_mail_from": None,
            "smtp_mail_to": None,
            "smtp_ssl_tls": None,
            "smtp_starttls": None,
            "webhook_url": None,
        },
    )

    assert response.status_code == 200
    assert response.json["message"] == "Configuration saved successfuly"
