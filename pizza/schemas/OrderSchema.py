from pydantic import BaseModel
from typing import Optional


class PlaceOrder(BaseModel):
    quantity: int
    pizza_size: str

class ViewOrder(BaseModel):
    id: int
    quantity: int
    order_status: str
    pizza_size: str
    user_id: int

class UpdateStatus(BaseModel):
    order_status: str


    
