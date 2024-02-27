from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from db.core import Base, get_db
from db.user import get_current_user
from app import app
from fastapi.testclient import TestClient
from fastapi import status

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    """
    Overrides the get_current_user function to return a testing user
    """
    username = 'admin'
    role = 'admin'
    user_id = 1
    return {"username": username, "id": user_id, 'role': role}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_read_all_authenticated():
    response = client.get("/api/invoices")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
