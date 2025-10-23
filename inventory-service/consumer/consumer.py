'''
order_created --> call update product api
order_canceled --> call update product api

send source_event_name in payload
'''

from aiokafka import AIOKafkaConsumer
import json, asyncio
import requests

inventory_svc_base_url = "http://inventory-ms:8000/products"

event_id_processed = []


async def consume():
    consumer = AIOKafkaConsumer(
    "mongo.order.outbox",
    bootstrap_servers="kafka:9092",
    group_id = "inventory-consumer",
    enable_auto_commit=False,
    auto_offset_reset="earliest")

    await consumer.start()

    try:
        while True:
            msg = await consumer.getone()
            try:
                data = json.loads(msg.value.decode())
                data = json.loads(data["payload"]["after"])
                if data["event_id"] not in event_id_processed:
                    event_id_processed.append(data["event_id"])
                    print(data)
                    payload = {}
                    product_id = data["products"][0]["product_id"]
                    payload["order_id"] = data["order_id"]
                    payload["qty"] = data["products"][0]["qty"]
                    payload["source_event_name"] = data["event_name"]
                    inventory_svc_url = f"{inventory_svc_base_url}/{product_id}"
                    response = requests.post(url=inventory_svc_url,json=payload)
                    print(response.json())
                else:
                    print("duplicate event")
                await consumer.commit()
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)    

if __name__ == "__main__":
    asyncio.run(consume())