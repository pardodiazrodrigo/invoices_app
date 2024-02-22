from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from db.core import NotFoundError, InvoiceDB
from fastapi import HTTPException


class Invoice(BaseModel):
    id: int
    invoice_number: str
    date: str
    cuit: str
    client: str
    amount: float
    user_id: int
    paid: bool


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(max_length=11, min_length=11)
    date: str = Field(max_length=10, min_length=10)
    cuit: str = Field(max_length=11, min_length=11)
    client: str = Field(max_length=50, min_length=1)
    amount: float = Field(gt=0)
    paid: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "0001-000150",
                "date": "2024-02-20",
                "cuit": "20345678901",
                "client": "Empresa A S.A.",
                "amount": 722.50,
                "paid": False
            }
        }


class InvoiceUpdate(BaseModel):
    id: int = Field(gt=0)
    invoice_number: Optional[str] = Field(max_length=11, min_length=11)
    date: Optional[str] = Field(max_length=10, min_length=10)
    cuit: Optional[str] = Field(max_length=11, min_length=11)
    client: Optional[str] = Field(max_length=50, min_length=1)
    amount: Optional[float] = Field(gt=0)
    paid: Optional[bool] = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "invoice_number": "0001-000150",
                "date": "2024-02-20",
                "cuit": "20345678901",
                "client": "Updated A S.A.",
                "amount": 722.50,
                "paid": False
            }
        }


def create_db_invoice(invoice: InvoiceCreate, session: Session, user_id: int):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized ss")
    db_invoice = InvoiceDB(**invoice.model_dump(), user_id=user_id)
    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)

    return db_invoice


def read_db_invoice(invoice_id: int, session: Session, user_id: int):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_invoice = (session.query(InvoiceDB).filter(InvoiceDB.id == invoice_id)
                  .filter(InvoiceDB.user_id == user_id).first())

    if not db_invoice:
        raise NotFoundError(f"Invoice with id {invoice_id} not found")

    return db_invoice


def update_db_invoice(invoice_id: int, invoice: InvoiceUpdate, session: Session, user_id: int):
    db_invoice = read_db_invoice(invoice_id, session, user_id)
    for key, value in invoice.model_dump().items():
        setattr(db_invoice, key, value)

    session.commit()
    session.refresh(db_invoice)

    return None


def delete_db_invoice(invoice_id: int, session: Session, user_id: int):
    db_invoice = read_db_invoice(invoice_id, session, user_id)
    session.delete(db_invoice)
    session.commit()

    return None
