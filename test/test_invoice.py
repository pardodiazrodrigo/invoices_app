from db.core import get_db
from db.user import get_current_user
from app import app
from fastapi.testclient import TestClient
from fastapi import status
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


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
    response = client.get("/api/invoice?invoice_id=1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'client': 'Test A S.A.',
                               'invoice_number': '0002-000722',
                               'date': '2024-02-27',
                               'user_id': 1,
                               'id': 1,
                               'cuit': '20345678999',
                               'amount': 1122.5,
                               'paid': False}


def test_read_invoice_unauthenticated_not_found(test_invoice):
    response = client.get("/api/invoice?invoice_id=999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': "Not Found"}


def test_read_invoice_authenticated_user_id(test_invoice_user_id_2):
    response = client.get("/api/invoice?invoice_id=2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Not Found"
    }


def test_create_invoice(test_invoice):
    request_data = {
        "invoice_number": "0011-000722",
        "date": "2024-02-27",
        "cuit": "20345678999",
        "client": "Test A S.A.",
        "amount": 1122.50,
        "paid": False,
        "user_id": 10
    }
    response = client.post("/api/invoice", json=request_data)
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert invoice.invoice_number == "0011-000722"
    assert invoice.client == "Test A S.A."


def test_update_invoice(test_invoice):
    request_data = {
        "invoice_number": "0011-000722",
        "date": "2024-02-27",
        "cuit": "20345678999",
        "client": "Test A S.A.",
        "amount": 1122.50,
        "paid": True,
        "id": 1
    }
    respone = client.put("/api/invoice", json=request_data)
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 1).first()
    assert respone.status_code == status.HTTP_204_NO_CONTENT
    assert invoice.invoice_number == "0011-000722"
    assert invoice.paid is True


def test_update_invoice_not_found(test_invoice):
    request_data = {
        "invoice_number": "0011-000722",
        "date": "2024-02-27",
        "cuit": "20345678999",
        "client": "Test A S.A.",
        "amount": 1122.50,
        "paid": True,
        "id": 999
    }
    response = client.put("/api/invoice", json=request_data)
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 999).first()
    assert invoice is None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':  'Not Found'}


def test_delete_invoice(test_invoice):
    response = client.delete("/api/invoice?invoice_id=1")
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert invoice is None


def test_delete_invoice_not_found(test_invoice):
    response = client.delete("/api/invoice?invoice_id=999")
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 999).first()
    assert invoice is None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Not Found'}
