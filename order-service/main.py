from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import db_connection
from routes import order


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.create_connection()
    yield
    await db_connection.close_connection()



app = FastAPI(title="Order Service",lifespan=lifespan)
app.include_router(order.order_router)


@app.get("/healthcheck")
async def healthcheck():
    return {"Data": "order service running"}