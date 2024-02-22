from fastapi import FastAPI

from routers import admin, auth, invoices, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(invoices.router)
app.include_router(users.router)


@app.get("/",  tags=["Root"])
async def root():
    return {"message": "Server is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
