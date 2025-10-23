from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://mongo:27017"
DB_NAME = "inventory"
global client, db

async def create_connections(): 
    global client, db
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client[DB_NAME]
    print("MongoDB connected!")

async def close_connections():
    global client, db
    client.close()