ENDPOINT = "/api/auth/login"


def test__login__valid_data__200(test_flask_client):

    response = test_flask_client.post(ENDPOINT, json={"username": "admin", "password": "xss"})

    assert response.status_code == 200
    assert "access_token" in response.json.keys()


def test__login__already_logged_in__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"username": "admin", "password": "xss"})

    assert response.status_code == 400
    assert response.json["message"] == "Already logged in"


def test__login__missing_data__400(test_flask_client):

    response = test_flask_client.post(ENDPOINT, json={"username": "admin"})

    assert response.status_code == 400
    assert response.json["message"] == "Missing username or password"


def test__login__bad_password__400(test_flask_client):

    response = test_flask_client.post(ENDPOINT, json={"username": "admin", "password": "test"})

    assert response.status_code == 403
    assert response.json["message"] == "Bad username or password"
