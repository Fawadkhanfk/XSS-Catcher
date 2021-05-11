from app.models import Client
from tests.conftest import create_test_client

ENDPOINT = "/api/client/{id}"


def test__delete_client__valid_data__no_client(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.delete(ENDPOINT.format(id=1), headers=authorization_headers["access_header"])

    number_of_clients = Client.query.count()

    assert response.status_code == 200
    assert number_of_clients == 0


def test__delete_client__non_existing_user__404(test_flask_client, authorization_headers):

    response = test_flask_client.delete(ENDPOINT.format(id=1), headers=authorization_headers["access_header"])

    assert response.status_code == 404
