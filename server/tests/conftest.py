import os
from shutil import copyfile

import pytest
from xss import app

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASEDIR, "app_test.db")
app.config["TESTING"] = True


@pytest.fixture(scope="function")
def test_flask_client():

    setup_database("app_test.db.template")

    with app.test_client() as client:
        yield client

    os.remove(os.path.join(BASEDIR, "app_test.db"))


@pytest.fixture(scope="function")
def test_flask_client_with_empty_db():

    setup_database("app_test_empty.db.template")

    with app.test_client() as client:
        yield client

    os.remove(os.path.join(BASEDIR, "app_test.db"))


def setup_database(db_template_file_name):

    copyfile(os.path.join(BASEDIR, db_template_file_name), os.path.join(BASEDIR, "app_test.db"))


@pytest.fixture
def authorization_headers(test_flask_client):

    response = test_flask_client.post("/api/auth/login", json={"username": "admin", "password": "xss"}).json
    return {
        "access_header": {"Authorization": f"Bearer {response['access_token']}"},
        "refresh_header": {"Authorization": f"Bearer {response['refresh_token']}"},
    }


def create_test_client(test_flask_client, authorization_headers, client_name):

    test_flask_client.post("/api/client", headers=authorization_headers["access_header"], json={"name": client_name, "description": ""})


def create_test_user(test_flask_client, authorization_headers, username):

    test_flask_client.post("/api/user", headers=authorization_headers["access_header"], json={"username": username})


def create_test_settings(test_flask_client, authorization_headers, settings):

    test_flask_client.patch(
        "/api/settings",
        headers=authorization_headers["access_header"],
        json=settings,
    )
