ENDPOINT = "/api/auth/logout"


def test__logout__valid_data__200(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["refresh_header"])

    assert response.status_code == 200
    assert response.json["message"] == "Logged out successfully"
