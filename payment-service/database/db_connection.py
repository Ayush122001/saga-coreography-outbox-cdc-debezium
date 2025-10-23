from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://mongo:27017"
DB_NAME = "payment"
global client, db

async def create_connection():
    global client, db
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    print("Mongo Connected")

async def close_connection():
    global client, db
    client.close()