from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from db.core import Base, get_db
from db.user import get_current_user
from app import app
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from db.core import InvoiceDB

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


@pytest.fixture
def test_invoice():
    invoice = InvoiceDB(
        invoice_number="0002-000722",
        date= "2024-02-27",
        cuit="20345678999",
        client="Test A S.A.",
        amount=1122.50,
        paid=False,
        user_id=1,
    )

    db = TestingSessionLocal()
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    yield invoice

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM invoice;"))
        conn.commit()


def test_read_all_authenticated(test_invoice):
    response = client.get("/api/invoices")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'client': 'Test A S.A.',
                                'invoice_number': '0002-000722',
                                'date': '2024-02-27',
                                'user_id': 1,
                                'id': 1,
                                'cuit': '20345678999',
                                'amount': 1122.5,
                                'paid': False}]


def test_read_invoice_authenticated(test_invoice):
    response = client.get("/api/invoice?id=1")
    assert response.status_code == status.HTTP_200_OK, "No dio 200?"
    assert response.json() == {'client': 'Test A S.A.',
                               'invoice_number': '0002-000722',
                               'date': '2024-02-27',
                               'user_id': 1,
                               'id': 1,
                               'cuit': '20345678999',
                               'amount': 1122.5,
                               'paid': False}
