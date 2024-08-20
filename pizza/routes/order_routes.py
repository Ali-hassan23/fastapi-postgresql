from fastapi import APIRouter,HTTPException,status,Depends
from schemas.OrderSchema import ViewOrder,PlaceOrder, UpdateStatus
from sqlalchemy.orm import Session
from typing import Annotated,List

from db import SessionLocal
from models import Orders, User
from routes.auth_routes import get_current_user, get_active_staff


order_router = APIRouter(
    prefix='/order'
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@order_router.get('/', response_model=List[ViewOrder], status_code=status.HTTP_200_OK)
def ViewOrders(current_user: Annotated[User, Depends(get_current_user)], db : Session = Depends(get_db)):
    return db.query(Orders).filter(Orders.user_id == current_user.id).all()


@order_router.post('/', response_model=ViewOrder, status_code=status.HTTP_201_CREATED)
def placeOrder(order : PlaceOrder,current_user: Annotated[User, Depends(get_current_user)], db : Session = Depends(get_db)):
    new_order = Orders(
        quantity = order.quantity,
        order_status = 'PENDING',
        pizza_size = order.pizza_size.upper(),
        user_id = current_user.id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@order_router.put('/{order_id}', response_model=ViewOrder, status_code=status.HTTP_200_OK)
def update_order_status(update : UpdateStatus, order_id : int ,staff : Annotated[User,Depends(get_active_staff)], db : Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.id == order_id and Orders.order_status == 'PENDING').first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.order_status = update.order_status
    return order
