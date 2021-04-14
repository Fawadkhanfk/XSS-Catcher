ENDPOINT = "/api/auth/refresh"


def test__refresh_token__valid_data__200(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["refresh_header"])

    assert response.status_code == 200
    assert "access_token" in response.json.keys()
