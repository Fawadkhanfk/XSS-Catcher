ENDPOINT = "/api/settings"


def test__edit_settings__valid_data__200(test_flask_client, authorization_headers):

    test_data = {
        "smtp_host": "smtp.hackerman.ca",
        "smtp_port": 587,
        "smtp_user": "test",
        "smtp_pass": "test",
        "smtp_mail_from": "xss-catcher@hackerman.ca",
        "smtp_mail_to": "dax@hackerman.ca",
        "smtp_ssl_tls": True,
        "webhook_url": "https://hackerman.ca",
    }

    response = test_flask_client.patch(ENDPOINT, headers=authorization_headers["access_header"], json=test_data)

    assert response.status_code == 200
    assert response.json["message"] == "Configuration saved successfuly"
