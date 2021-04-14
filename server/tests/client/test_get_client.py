from tests.conftest import create_test_client

ENDPOINT = "/api/client"


def test__get_client__valid_data__200(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.get(f"{ENDPOINT}/1", headers=authorization_headers["access_header"])

    assert response.status_code == 200
    assert response.json["name"] == "test"


def test__get_client__non_existing_client__404(test_flask_client, authorization_headers):

    response = test_flask_client.get(f"{ENDPOINT}/1", headers=authorization_headers["access_header"])

    assert response.status_code == 404
