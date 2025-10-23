'''
order_return --> Call update payment
send source_event_name in payload
'''

from aiokafka import AIOKafkaConsumer
import json, asyncio
import requests

payment_svc_base_url = "http://payment-ms:8000/payments"

event_id_processed = []

async def consume():
    consumer = AIOKafkaConsumer(
    "mongo.order.outbox",
    bootstrap_servers="kafka:9092",
    group_id = "payment-consumer",
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
                    payment_svc_url = f"{payment_svc_base_url}/{order_id}"
                    response = requests.post(url=payment_svc_url,json=payload)
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