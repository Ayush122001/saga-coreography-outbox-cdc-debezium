from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import products
from database import db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.create_connections()
    yield
    await db_connection.close_connections()


app = FastAPI(title="Inventory Service",lifespan=lifespan)

app.include_router(products.product_router)

@app.get("/healthcheck")
async def healthcheck():
    return {"Data": "inventory service running"}