from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    product_id: str
    price: float
    qty: int
    name: str


class CreateOrder(BaseModel):
    order_id: Optional[str] = None
    order_amt: Optional[float] = None
    products: list[Product] 

class UpdateOrder(BaseModel):
    order_id: str
    source_event_name: str