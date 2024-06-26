from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from decouple import config

SQLALCHEMY_DB_URL = config("DATABASE_URL")


class Base(DeclarativeBase):
    pass


class NotFoundError(Exception):
    pass


class UserDB(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")
    phone_number: Mapped[str] = mapped_column(default="")


class InvoiceDB(Base):
    __tablename__ = "invoice"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    invoice_number: Mapped[str]
    date: Mapped[str]
    cuit: Mapped[str]
    client: Mapped[str]
    amount: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    paid: Mapped[bool] = mapped_column(default=False)


engine = create_engine(SQLALCHEMY_DB_URL)
sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
