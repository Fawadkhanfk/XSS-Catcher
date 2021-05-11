from tests.conftest import create_test_user

ENDPOINT = "/api/user/{id}/password"


def test__reset_user_password__valid_data__200(test_flask_client, authorization_headers):

    create_test_user(test_flask_client, authorization_headers, "test")

    response = test_flask_client.post(ENDPOINT.format(id=2), headers=authorization_headers["access_header"])

    assert response.status_code == 200
    assert "message" in response.json.keys()


def test__reset_user_password__non_existing_user__404(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT.format(id=2), headers=authorization_headers["access_header"])

    assert response.status_code == 404
