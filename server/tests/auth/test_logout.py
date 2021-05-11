ENDPOINT = "/api/auth/logout"


def test__logout__valid_data__token_invalidated(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["refresh_header"])

    invalid_token_response = test_flask_client.post("/api/auth/refresh", headers=authorization_headers["refresh_header"])

    assert response.status_code == 200
    assert invalid_token_response.status_code == 401
    assert invalid_token_response.json["msg"] == "Token has been revoked"
