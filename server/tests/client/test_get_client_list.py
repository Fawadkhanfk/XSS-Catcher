from tests.conftest import create_test_client


def test__get_client_list__valid_data__200(test_flask_client, authorization_headers):

    create_test_client(test_flask_client, authorization_headers, "test1")
    create_test_client(test_flask_client, authorization_headers, "test2")

    response = test_flask_client.get("/api/client", headers=authorization_headers["access_header"])

    assert response.status_code == 200
    assert len(response.json) == 2
