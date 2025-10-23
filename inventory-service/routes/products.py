from fastapi import APIRouter, Request
from models.models import Product, UpdateProduct
from database import db_connection
import uuid
from bson import json_util
import json

product_router = APIRouter(prefix='/products',tags=['products'])

# List all products
@product_router.get("/")
async def get_products():
    all_products = await db_connection.db["products"].find().to_list(length=None)
    return json.loads(json_util.dumps(all_products))

# List single products
@product_router.get("/{product_id}")
async def get_single_product(product_id: str):
    result = await db_connection.db["products"].find_one({"product_id": product_id})
    return json.loads(json_util.dumps(result))

# Create product
@product_router.post("/")
async def create_products(product_obj: Product):
    random_part = uuid.uuid4().hex[:6]
    product_id = f"product-{random_part}"
    product_obj.product_id = product_id
    data = product_obj.model_dump()
    async with await db_connection.client.start_session() as session:
        async with session .start_transaction():
            result = await db_connection.db["products"].insert_one(data)
    inserted_product = await db_connection.db["products"].find_one({"product_id": product_id})
    return json.loads(json_util.dumps(inserted_product))

# Update product (Handels event)
@product_router.post("/{product_id}")
async def update_products(updated_product: UpdateProduct, product_id: str):
    update_data = updated_product.model_dump(exclude_unset=True)

    # Geneate event id
    random_part = uuid.uuid4().hex[:6]
    update_data["event_id"] = f"event-{random_part}"

    # Event : order_created 
    if update_data["source_event_name"] == "order_created":
        async with await db_connection.client.start_session() as session:
            async with session .start_transaction():
                result = await db_connection.db["products"].find_one({"product_id": product_id})
                result = json.loads(json_util.dumps(result))
                if (result["qty"] - update_data["qty"]) < 0:
                    update_data["event_name"] = "reserve_inventory_failed"
                    final_event = await db_connection.db["outbox"].insert_one(update_data)
                else:
                    result["qty"] = result["qty"] - update_data["qty"]
                    result.pop("_id")
                    print(result)
                    data = await db_connection.db["products"].update_one({"product_id": product_id}, {"$set":result})  
                    update_data["event_name"] = "reserve_inventory"
                    final_event = await db_connection.db["outbox"].insert_one(update_data)
        result = await db_connection.db["outbox"].find_one({"event_id": f"event-{random_part}"})        
        return json.loads(json_util.dumps(result))
    
    # Event: order_canceled
    elif (update_data["source_event_name"] == "order_canceled") or (update_data["source_event_name"] == "order_failed") or (update_data["source_event_name"] == "order_return"):
        async with await db_connection.client.start_session() as session:
            async with session .start_transaction():
                result = await db_connection.db["products"].find_one({"product_id": product_id})
                result = json.loads(json_util.dumps(result))
                result["qty"] = result["qty"] + update_data["qty"]
                result.pop("_id")
                data = await db_connection.db["products"].update_one({"product_id": product_id}, {"$set":result})  
                update_data["event_name"] = "released_inventory"
                final_event = await db_connection.db["outbox"].insert_one(update_data)
        result = await db_connection.db["outbox"].find_one({"event_id": f"event-{random_part}"})        
        return json.loads(json_util.dumps(result))
    else:
        return {"Data": "Incorrect Event"}


# Delete product
@product_router.delete("/{product_id}")
async def delete_products(product_id: str):
    async with await db_connection.client.start_session() as session:
        async with session .start_transaction():
            result = await db_connection.db["products"].delete_one({"product_id": product_id})
    result = await db_connection.db["products"].find_one({"product_id": product_id})
    return json.loads(json_util.dumps(result))
