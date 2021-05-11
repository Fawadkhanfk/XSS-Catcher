import jwt
from app import Config

ENDPOINT = "/api/auth/refresh"


def test__refresh_token__valid_data__valid_token(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["refresh_header"])

    decoded_access_token = jwt.decode(response.json["access_token"], algorithms=["HS256"], key=Config.SECRET_KEY)

    assert response.status_code == 200
    assert decoded_access_token["sub"] == "admin"
    assert decoded_access_token["type"] == "access"
