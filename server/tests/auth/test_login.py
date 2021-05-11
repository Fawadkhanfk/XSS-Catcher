import jwt
from app import Config

ENDPOINT = "/api/auth/login"


def test__login__valid_data__200(test_flask_client):

    response = test_flask_client.post(ENDPOINT, json={"username": "admin", "password": "xss"})

    decoded_access_token = jwt.decode(response.json["access_token"], algorithms=["HS256"], key=Config.SECRET_KEY)
    decoded_refresh_token = jwt.decode(response.json["refresh_token"], algorithms=["HS256"], key=Config.SECRET_KEY)

    assert response.status_code == 200
    assert decoded_access_token["sub"] == "admin"
    assert decoded_refresh_token["sub"] == "admin"
    assert decoded_access_token["type"] == "access"
    assert decoded_refresh_token["type"] == "refresh"


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
