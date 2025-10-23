from fastapi import APIRouter
from models.models import CreateOrder, UpdateOrder
import uuid
from database import db_connection
from bson import json_util
import json

order_router = APIRouter(prefix="/orders",tags=["orders"])

# List all order
@order_router.get("/")
async def get_order():
    all_orders = await db_connection.db["order"].find().to_list(length=None)
    return json.loads(json_util.dumps(all_orders))

# List single order
@order_router.get("/{order_id}")
async def get_single_order(order_id: str):
    orders = await db_connection.db["order"].find_one({"order_id": order_id})
    return json.loads(json_util.dumps(orders))


# Create Order
@order_router.post("/")
async def create_order(order_obj: CreateOrder):
    random_part = uuid.uuid4().hex[:6]
    order_id = f"order-{random_part}"
    order_obj = order_obj.model_dump()
    # Adding order id
    order_obj["order_id"] = order_id
    # Computing order Amt
    order_amt = 0
    for i in order_obj["products"]:
        order_amt = order_amt + (i["qty"] * i["price"])
    order_obj["order_amt"] = order_amt
    # adding status
    order_obj["status"] = "pending"

    async with await db_connection.client.start_session() as session:
        async with session.start_transaction():
            result = await db_connection.db["order"].insert_one(order_obj)
            # writing to outbox
            event_name = "order_created"
            random_part = uuid.uuid4().hex[:6]
            event_id = f"event-{random_part}"
            order_obj["event_name"] = event_name
            order_obj["event_id"] = event_id
            result = await db_connection.db["outbox"].insert_one(order_obj)
    inserted_order = await db_connection.db["order"].find_one({"order_id": order_id})
    return (json.loads(json_util.dumps(inserted_order)))

# Delete Order
@order_router.delete("/{order_id}")
async def delete_order(order_id: str):
    async with await db_connection.client.start_session() as session:
        async with session .start_transaction():
            result = await db_connection.db["order"].delete_one({"order_id": order_id})
    result = await db_connection.db["order"].find_one({"order_id": order_id})
    return json.loads(json_util.dumps(result))

# Update Order
@order_router.post("/{order_id}")
async def update_order(order_id: str, order_obj: UpdateOrder):
    random_part = uuid.uuid4().hex[:6]
    order_obj = order_obj.model_dump()
    if order_obj["source_event_name"] == "reserve_inventory_failed":
        async with await db_connection.client.start_session() as session:
          async with session .start_transaction():
            result = await db_connection.db["order"].update_one({"order_id": order_obj["order_id"]},{"$set":{"status": "canceled"}})
            result = await db_connection.db["order"].find_one({"order_id": order_obj["order_id"]})
            result = json.loads(json_util.dumps(result))
            order_obj["event_name"] = "order_failed_inventory_issue"
            order_obj["event_id"] = f"event-{random_part}"
            order_obj["products"] = result["products"]
            order_obj["order_amt"] = result["order_amt"]
            final_event = await db_connection.db["outbox"].insert_one(order_obj)
        result = await db_connection.db["order"].find_one({"order_id": order_id}) 
        return json.loads(json_util.dumps(result))
    elif order_obj["source_event_name"] == "payment_success":
        async with await db_connection.client.start_session() as session:
          async with session .start_transaction():
            result = await db_connection.db["order"].update_one({"order_id": order_obj["order_id"]},{"$set":{"status": "completed"}})
            result = await db_connection.db["order"].find_one({"order_id": order_obj["order_id"]})
            result = json.loads(json_util.dumps(result))
            order_obj["event_name"] = "order_completed"
            order_obj["event_id"] = f"event-{random_part}"
            order_obj["products"] = result["products"]
            order_obj["order_amt"] = result["order_amt"]
            final_event = await db_connection.db["outbox"].insert_one(order_obj)
        result = await db_connection.db["order"].find_one({"order_id": order_id}) 
        return json.loads(json_util.dumps(result))
    elif order_obj["source_event_name"] == "payment_failed":
        async with await db_connection.client.start_session() as session:
          async with session .start_transaction():
            result = await db_connection.db["order"].update_one({"order_id": order_obj["order_id"]},{"$set":{"status": "failed"}})
            result = await db_connection.db["order"].find_one({"order_id": order_obj["order_id"]})
            result = json.loads(json_util.dumps(result))
            order_obj["event_name"] = "order_failed"
            order_obj["event_id"] = f"event-{random_part}"
            order_obj["products"] = result["products"]
            order_obj["order_amt"] = result["order_amt"]
            final_event = await db_connection.db["outbox"].insert_one(order_obj)
        result = await db_connection.db["order"].find_one({"order_id": order_id}) 
        return json.loads(json_util.dumps(result))
    else:
        return {"Data": "Incorrect Event"}
    
@order_router.post("/return/{order_id}")
async def return_order(order_id: str):
    random_part = uuid.uuid4().hex[:6]
    async with await db_connection.client.start_session() as session:
          async with session .start_transaction():
            result = await db_connection.db["order"].update_one({"order_id": order_id},{"$set":{"status": "returned"}})
            result = await db_connection.db["order"].find_one({"order_id": order_id})
            result = json.loads(json_util.dumps(result))
            result.pop("_id")
            result["event_name"] = "order_return"
            result["event_id"] = f"event-{random_part}"
            final_event = await db_connection.db["outbox"].insert_one(result)
    result = await db_connection.db["order"].find_one({"order_id": order_id})
    return json.loads(json_util.dumps(result))
