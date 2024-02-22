from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.core import get_db, InvoiceDB
from db.user import user_dependency
from starlette import status

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/invoices", status_code=status.HTTP_200_OK)
async def read_all_invoices(user: user_dependency, db: Session = Depends(get_db)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(InvoiceDB).all()


@router.delete("/invoice", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(user: user_dependency, invoice_id: int = Query(gt=0), db: Session = Depends(get_db)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorized")
    invoice_db = db.query(InvoiceDB).filter(InvoiceDB.id == invoice_id).first()
    if not invoice_db:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(invoice_db)
    db.commit()
