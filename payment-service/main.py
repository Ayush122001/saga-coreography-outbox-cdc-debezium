from fastapi import FastAPI

from contextlib import asynccontextmanager
from database import db_connection
from routes import payment


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.create_connection()
    yield
    await db_connection.close_connection()



app = FastAPI(title="Payment Service",lifespan=lifespan)
app.include_router(payment.payment_router)
@app.get("/healthcheck")
async def healthcheck():
    return {"Data": "payment service running"}