from unittest import mock

ENDPOINT = "/api/settings/test/webhook"


@mock.patch("requests.post")
def test__test_webhook_settings__valid_data__200(post_mocker, test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"url": "https://hackerman.ca"})

    assert response.status_code == 200
    assert response.json["message"] == "Webhook configuration test successful"


def test__test_webhook_settings__missing_url__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"url": ""})

    assert response.status_code == 400
    assert response.json["message"] == "Missing URL"


def test__test_webhook_settings__invalid_url__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"url": "test"})

    assert response.status_code == 400
    assert response.json["message"] == "Invalid URL"


@mock.patch("requests.post", side_effect=ValueError)
def test__test_webhook_settings__fail_to_send_hook__500(post_mocker, test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"url": "https://hackerman.ca"})

    assert response.status_code == 500
    assert response.json["message"] == "Could not send test webhook"
