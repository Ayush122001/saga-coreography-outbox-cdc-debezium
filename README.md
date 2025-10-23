# 🧩 Saga Choreography + Outbox + CDC (Debezium + MongoDB + Kafka)

This repository demonstrates a complete **event-driven microservices architecture** using:

- **Saga Pattern (Choreography)**
- **Outbox Pattern** for atomic event publishing
- **Change Data Capture (CDC)** via **Debezium**
- **Asynchronous communication** using **Apache Kafka**
- **Database-per-Service** principle with **MongoDB**
- **Kong Gateway** for unified API access

It’s designed to give a *real working example* of distributed data consistency, failure handling, and event-driven design , not just theory.

## All API endpoints are included in the Postman collection. You can access it [![Postman Collection](https://img.shields.io/badge/Postman-Collection-orange)](./microservice-project.postman_collection.json)

---

## 🚀 Quick Start (Everything in One Go)

### 1️⃣ Clone Repository
```
git clone https://github.com/Ayush122001/saga-coreography-outbox-cdc-debezium.git
cd saga-coreography-outbox-cdc-debezium
```
### 2️⃣ Start the Stack
```docker compose up -d```
This starts everything: MongoDB (replica set), Apache Kafka + Zookeeper, Debezium (Kafka Connect), Kong Gateway, Kafka UI, all microservices (Order, Inventory, Payment), and all event consumers.

🧠 NOTE: On first run, some services may fail because Mongo databases, collections, and Debezium connectors are not yet created. That’s expected , continue with the steps below.

⚙️ One-Time Initialization (First Run Setup)

## 🗄️ Step 1 , Create Mongo Databases & Collections

Connect to MongoDB(or via compass):
```docker exec -it mongo mongosh```

Inside Mongo shell, run:
```// Inventory DB
use inventory
db.createCollection("products")
db.createCollection("outbox")

// Order DB
use order
db.createCollection("order")
db.createCollection("outbox")

// Payment DB
use payment
db.createCollection("payment")
db.createCollection("outbox")
Exit Mongo shell:
exit
```

## 🔗 Step 2 , Create Debezium Connectors
Use Postman or curl to create connectors.

POST URL: 
``` http://localhost:8083/connectors
Header: Content-Type: application/json


Order Connector
{
  "name": "order-event-connector",
  "config": {
    "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
    "mongodb.connection.string": "mongodb://mongo:27017/?replicaSet=rs0",
    "topic.prefix": "mongo",
    "collection.include.list": "order.outbox",
    "snapshot.mode": "initial",
    "tasks.max": "1"
  }
}

Inventory Connector
{
  "name": "inventory-event-connector",
  "config": {
    "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
    "mongodb.connection.string": "mongodb://mongo:27017/?replicaSet=rs0",
    "topic.prefix": "mongo",
    "collection.include.list": "inventory.outbox",
    "snapshot.mode": "initial",
    "tasks.max": "1"
  }
}

Payment Connector
{
  "name": "payment-event-connector",
  "config": {
    "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
    "mongodb.connection.string": "mongodb://mongo:27017/?replicaSet=rs0",
    "topic.prefix": "mongo",
    "collection.include.list": "payment.outbox",
    "snapshot.mode": "initial",
    "tasks.max": "1"
  }
}
```

## 🔁 Step 3 , Restart Everything
```docker compose up -d```
✅ Stack will now start successfully with all connectors registered and event propagation working.


### 🧪 Test the System
Use the provided Postman collection to test full flows.

Example Scenarios:
```
Order creation → Inventory unavailable → Order cancelled

Order creation → Inventory reserved → Payment failed → Order failed → Inventory released

Order creation → Inventory reserved → Payment success → Order completed

Return order → Payment refund → Inventory released

Use Kong Gateway for all APIs: http://localhost:8000
```

### ⚙️ Common Commands
## View Logs
```docker compose logs -f order-service```

## Restart a Single Service
```docker compose restart payment-service```

## Stop All Containers
```docker compose down```

## Clean All Containers, Volumes, and Networks
``` docker compose down -v```
