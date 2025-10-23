'''
reserve_inventory_failed --> update order
payment_failed --> updated order
'''

from aiokafka import AIOKafkaConsumer
import json, asyncio
import requests

order_svc_base_url = "http://order-ms:8000/orders"

event_id_processed = []

async def consume():
    consumer = AIOKafkaConsumer(
    "mongo.inventory.outbox",
    "mongo.payment.outbox",
    bootstrap_servers="kafka:9092",
    group_id = "order-consumer",
    enable_auto_commit=False,
    auto_offset_reset="earliest")

    await consumer.start()

    try:
        while True:
            msg = await consumer.getone()
            try:
                data = json.loads(msg.value.decode())
                data = json.loads(data["payload"]["after"])
                print(msg.topic)
                if data["event_id"] not in event_id_processed:
                    event_id_processed.append(data["event_id"])
                    print(data)
                    payload = {}
                    order_id = data["order_id"]
                    payload["order_id"] = data["order_id"]
                    payload["source_event_name"] = data["event_name"]
                    order_svc_url = f"{order_svc_base_url}/{order_id}"
                    response = requests.post(url=order_svc_url,json=payload)
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