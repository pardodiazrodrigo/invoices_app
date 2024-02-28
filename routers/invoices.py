from fastapi import APIRouter, Query, HTTPException, Depends
from starlette import status
from db.core import get_db, InvoiceDB, NotFoundError
from sqlalchemy.orm import Session
from db.invoice import (create_db_invoice,
                        read_db_invoice,
                        update_db_invoice,
                        delete_db_invoice,
                        Invoice, InvoiceCreate, InvoiceUpdate)
from db.user import user_dependency

router = APIRouter(
    prefix="/api",
    tags=["Invoices"],
)


@router.get("/invoices", status_code=status.HTTP_200_OK)
async def read_all_invoices(user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        return db.query(InvoiceDB).filter(InvoiceDB.user_id == user.get('id')).all()
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e


@router.post("/invoice",  status_code=status.HTTP_201_CREATED)
async def create_invoice(user: user_dependency, invoice: InvoiceCreate, db: Session = Depends(get_db)):
    try:
        db_invoice = create_db_invoice(invoice, db, user.get('id'))
    except Exception as e:
        raise HTTPException(status_code=500) from e
    return Invoice(**db_invoice.__dict__)


@router.get("/invoice/{invoice_id}", status_code=status.HTTP_200_OK)
async def read_invoice(user: user_dependency, invoice_id: int, db: Session = Depends(get_db)):
    try:
        db_invoice = read_db_invoice(invoice_id, db, user.get('id'))
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Invoice(**db_invoice.__dict__)


@router.put("/invoice", status_code=status.HTTP_204_NO_CONTENT)
async def update_invoice(user: user_dependency, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    try:
        update_db_invoice(invoice.id, invoice, db, user.get('id'))
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e


@router.delete("/invoice", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(user: user_dependency, invoice_id: int = Query(gt=0), db: Session = Depends(get_db)):
    try:
        delete_db_invoice(invoice_id, db, user.get('id'))
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
