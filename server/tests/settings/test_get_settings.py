ENDPOINT = "/api/settings"


def test__get_settings__valid_request__200(test_flask_client, authorization_headers):

    response = test_flask_client.get(ENDPOINT, headers=authorization_headers["access_header"])

    assert response.status_code == 200
    assert "smtp_host" in response.json.keys()
