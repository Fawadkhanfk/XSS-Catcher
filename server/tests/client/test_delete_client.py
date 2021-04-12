from tests.conftest import create_test_client


def test__delete_client__valid_data__200(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.delete("/api/client/1", headers=authorization_headers["access_header"])

    assert response.status_code == 200
    assert response.json["message"] == "Client test deleted successfuly"


def test__delete_client__non_existing_user__404(test_flask_client, authorization_headers):

    response = test_flask_client.delete("/api/client/1", headers=authorization_headers["access_header"])

    assert response.status_code == 404
