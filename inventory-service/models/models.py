from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    name: str
    qty: int
    price: float
    product_id: Optional[str] = None

class UpdateProduct(BaseModel):
    order_id: str
    source_event_name: str
    qty: int