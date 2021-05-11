from app.models import Client
from tests.conftest import create_test_client

ENDPOINT = "/api/client"


def test__create_client__valid_data__new_client(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"name": "test", "description": "test"})

    number_of_clients = Client.query.count()

    assert response.status_code == 201
    assert number_of_clients == 1


def test__create_client__missing_client_name__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"name": "", "description": ""})

    assert response.status_code == 400
    assert response.json["message"] == "Missing client name"


def test__create_client__missing_description__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"name": "test"})

    assert response.status_code == 400
    assert response.json["message"] == "Missing description"


def test__create_client__existing_client__400(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"name": "test", "description": ""})

    assert response.status_code == 400
    assert response.json["message"] == "Client already exists"
