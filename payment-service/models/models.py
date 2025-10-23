from pydantic import BaseModel
from typing import Optional

class Payment(BaseModel):
    order_id: str
    payment_status: str # DONE or FAILED

class RefundPayment(BaseModel):
    order_id: str
    source_event_name: str 
