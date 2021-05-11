ENDPOINT = "/api/user"


def test__create_user__valid_data__200(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"username": "user"})

    assert response.status_code == 200
    assert "message" in response.json.keys()


def test__create_user__missing_username__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"username": ""})

    assert response.status_code == 400
    assert response.json["message"] == "Missing username"


def test__create_user__existing_user__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"username": "admin"})

    assert response.status_code == 400
    assert response.json["message"] == "This user already exists"
