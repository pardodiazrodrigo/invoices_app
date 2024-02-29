from .utils import *
from db.core import get_db
from db.user import get_current_user
from app import app
from fastapi.testclient import TestClient
from routers.auth import authenticate_user
from db.user import SECRET_KEY, ALGORITHM, create_access_token
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_auth_user(test_user):
    db = TestingSessionLocal()
    user = authenticate_user(test_user.username,  "test123", db)
    assert user is not None
    assert user.username == test_user.username

    wrong_user = authenticate_user("non_existener_user", "test123", db)
    assert wrong_user is False

    wrong_user_password = authenticate_user(test_user.username, "wrong_password", db)
    assert wrong_user_password is False


def test_create_access_token():
    username = "test123"
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    encode = {
        'sub': test_user.username,
        'id': test_user.id,
        'role': test_user.role
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token)
    assert user is not None
    assert user == {
        'id': test_user.id,
        'username': test_user.username,
        'role': test_user.role
    }


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    encode = {
        'sub': test_user.username,
        'id': test_user.id,
        'role': test_user.role
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token)
    assert user is not None
    assert user == {
        'id': test_user.id,
        'username': test_user.username,
        'role': test_user.role
    }


@pytest.mark.asyncio
async def test_get_current_user_not_found(test_user):
    encode = {
        'role': test_user.role
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
