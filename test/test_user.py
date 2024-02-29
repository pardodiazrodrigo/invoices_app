from .utils import *
from db.core import get_db
from db.user import get_current_user
from app import app
from fastapi.testclient import TestClient
from fastapi import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_return_user(test_user):
    response = client.get("/user/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == test_user.username
    assert response.json()['email'] == test_user.email
