ENDPOINT = "/api/user/password"


def test__change_current_user_password__valid_data__200(test_flask_client, authorization_headers):

    response = test_flask_client.post(
        ENDPOINT, headers=authorization_headers["access_header"], json={"old_password": "xss", "password1": "Password123!", "password2": "Password123!"}
    )

    assert response.status_code == 200
    assert response.json["message"] == "Password changed successfuly"


def test__change_current_user_password__missing_data__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(ENDPOINT, headers=authorization_headers["access_header"], json={"password1": "Password123!", "password2": "Password123!"})

    assert response.status_code == 400
    assert response.json["message"] == "Missing data"


def test__change_current_user_password__weak_password__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(
        ENDPOINT, headers=authorization_headers["access_header"], json={"old_password": "xss", "password1": "test", "password2": "test"}
    )

    assert response.status_code == 400
    assert response.json["message"] == "Password must be at least 8 characters and contain a uppercase letter, a lowercase letter and a number"


def test__change_current_user_password__new_passwords_mismatch__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(
        ENDPOINT, headers=authorization_headers["access_header"], json={"old_password": "xss", "password1": "Password123!", "password2": "Wrong123!"}
    )

    assert response.status_code == 400
    assert response.json["message"] == "Passwords don't match"


def test__change_current_user_password__wrong_password__400(test_flask_client, authorization_headers):

    response = test_flask_client.post(
        ENDPOINT, headers=authorization_headers["access_header"], json={"old_password": "test", "password1": "Password123!", "password2": "Password123!"}
    )

    assert response.status_code == 400
    assert response.json["message"] == "Old password is incorrect"
