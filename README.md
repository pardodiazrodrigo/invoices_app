FastAPI Invoices APP

## Installation

- Clone repository
- Add a .env file with these variables:
    * SECRET_KEY=
    * ALGORITHM=
    * DATABASE_URL
- pip install -r requirements.txt
- uvicorn app:app --reload
- to open Swagger docs: http://127.0.0.1:8000/doc
- to test de app:
    * pytest --disable-warnings  

