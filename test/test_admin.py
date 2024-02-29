from .utils import *
from db.core import get_db
from db.user import get_current_user
from app import app
from fastapi.testclient import TestClient
from fastapi import status
from db.core import InvoiceDB


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_admin_read_all_auth(test_invoice):
    response = client.get("/admin/invoices")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'client': 'Test A S.A.',
                                'invoice_number': '0002-000722',
                                'date': '2024-02-27',
                                'user_id': 1,
                                'id': 1,
                                'cuit': '20345678999',
                                'amount': 1122.5,
                                'paid': False}]


def test_read_all_invoices(test_invoice):
    response = client.get("/admin/invoices")
    assert response.status_code == status.HTTP_200_OK


def test_admin_delete_invoice(test_invoice):
    response = client.delete("/admin/invoice?invoice_id=1")
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert invoice is None


def test_admin_delete_invoice_not_found(test_invoice):
    response = client.delete("/admin/invoice?invoice_id=999")
    db = TestingSessionLocal()
    invoice = db.query(InvoiceDB).filter(InvoiceDB.id == 999).first()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert invoice is None
    assert response.json() == {'detail': 'Not found'}
