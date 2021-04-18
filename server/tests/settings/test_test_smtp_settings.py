from unittest import mock

from tests.conftest import create_test_settings

ENDPOINT = "/api/settings/test/smtp"


@mock.patch("smtplib.SMTP")
def test__test_smtp_settings__valid_data__200(SMTP_mocker, test_flask_client, authorization_headers):

    create_test_settings(
        test_flask_client,
        authorization_headers,
        {
            "smtp_host": "smtp.hackerman.ca",
            "smtp_port": 25,
            "smtp_mail_to": "dax@hackerman.ca",
        },
    )

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"mail_to": "dax@hackerman.ca"})

    assert response.status_code == 200
    assert response.json["message"] == "SMTP configuration test successful"


def test__test_smtp_settings__missing_recipient__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"mail_to": ""})

    assert response.status_code == 400
    assert response.json["message"] == "Missing recipient"


def test__test_smtp_settings__invalid_recipient__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"mail_to": "test"})

    assert response.status_code == 400
    assert response.json["message"] == "Invalid recipient"


@mock.patch("smtplib.SMTP", side_effect=ValueError)
def test__test_smtp_settings__invalid_smtp_configuration__500(SMTP_mocker, test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"mail_to": "dax@hackerman.ca"})

    assert response.status_code == 500
    assert response.json["message"] == "Could not send test email. Please review your SMTP configuration and don't forget to save it before testing it."
