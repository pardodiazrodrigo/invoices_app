from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
import pytest
from db.core import InvoiceDB, UserDB, Base
from db.user import bcrypt_context

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
    username = 'user'
    role = 'admin'
    user_id = 1
    return {"username": username, "id": user_id, 'role': role}


@pytest.fixture
def test_invoice():
    invoice = InvoiceDB(
        invoice_number="0002-000722",
        date="2024-02-27",
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


@pytest.fixture
def test_invoice_user_id_2():
    invoice = InvoiceDB(
        invoice_number="0002-000722",
        date="2024-02-27",
        cuit="20345678999",
        client="Test A S.A.",
        amount=1122.50,
        paid=False,
        user_id=2,
    )

    db = TestingSessionLocal()
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    yield invoice

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM invoice;"))
        conn.commit()


@pytest.fixture
def test_user():
    user = UserDB(
        username="admin",
        hashed_password=bcrypt_context.hash("test123"),
        email="admin@mail.com",
        role="admin",
        first_name="admin",
        last_name="admin"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM user;"))
        conn.commit()
