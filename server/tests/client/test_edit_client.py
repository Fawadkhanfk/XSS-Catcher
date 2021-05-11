from tests.conftest import create_test_client, create_test_user

ENDPOINT = "/api/client/{id}"


def test__edit_client__valid_data__200(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")
    create_test_user(test_flask_client, authorization_headers, "test")

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"name": "test", "description": "123", "owner": 2, "mail_to": "test@hackerman.ca", "webhook_url": "https://hackerman.ca"},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Client test edited successfuly"


def test__edit_client__existing_client_name__400(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")
    create_test_client(test_flask_client, authorization_headers, "test2")

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"name": "test2"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Another client already uses this name"


def test__edit_client__non_existing_user__400(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"owner": "2"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "This user does not exist"


def test__edit_client__empty_mail_to_and_webhook_url__200(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"mail_to": "", "webhook_url": ""},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Client test edited successfuly"


def test__edit_client__invalid_webhook_url__400(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"webhook_url": "test"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Webhook URL format is invalid"


def test__edit_client__invalid_mail_to__400(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test")

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"mail_to": "test"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Invalid mail recipient"


def test__edit_client__non_existing_client__404(test_flask_client, authorization_headers):

    response = test_flask_client.patch(
        ENDPOINT.format(id=1),
        headers=authorization_headers["access_header"],
        json={"name": "test"},
    )

    assert response.status_code == 404
