from fastapi import APIRouter
from models.models import Payment, RefundPayment
import uuid
from database import db_connection
from bson import json_util
import json

payment_router = APIRouter(prefix="/payments",tags=["payments"])

# List all payments
@payment_router.get("/")
async def get_patments():
    all_payment = await db_connection.db["payment"].find().to_list(length=None)
    return json.loads(json_util.dumps(all_payment))

# List single payments
@payment_router.get("/{payment_id}")
async def get_single_payment(payment_id: str):
    payment = await db_connection.db["payment"].find_one({"payment_id": payment_id})
    return json.loads(json_util.dumps(payment))

# Create payments
@payment_router.post("/")
async def create_payment(payment_obj: Payment):
    random_part = uuid.uuid4().hex[:6]
    payment_id = f"payment-{random_part}"
    payment_obj = payment_obj.model_dump()
    payment_obj["payment_id"] = payment_id
    if payment_obj["payment_status"] == "DONE":
        event_name = "payment_success"
    else:
        event_name = "payment_failed"
    async with await db_connection.client.start_session() as session:
        async with session.start_transaction():
            result = await db_connection.db["payment"].insert_one(payment_obj)
            payment_obj["event_name"] = event_name
            random_part = uuid.uuid4().hex[:6]
            payment_obj["event_id"] = f"event-{random_part}"
            result = await db_connection.db["outbox"].insert_one(payment_obj)
    result = await db_connection.db["payment"].find_one({"payment_id": payment_id}) 
    return json.loads(json_util.dumps(result))

# Update payments
@payment_router.post("/{order_id}")
async def create_payment(payment_obj: RefundPayment, order_id: str):
    random_part = uuid.uuid4().hex[:6]
    payment_obj = payment_obj.model_dump()
    if payment_obj["source_event_name"] == "order_return":
        async with await db_connection.client.start_session() as session:
            async with session.start_transaction():
                await db_connection.db["payment"].update_one({"order_id":order_id},{"$set": {"payment_status": "refund"}})
        result = await db_connection.db["payment"].find_one({"order_id":order_id}) 
        return json.loads(json_util.dumps(result))
    else:
        {"Data": "Incorrect Event"}

    