from db import Base
from sqlalchemy import Column,Integer,String,Boolean,Text,ForeignKey,Enum
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key= True)
    username = Column(String,unique = True)
    email = Column(String,unique = True)
    password = Column(Text, nullable=False)
    is_staff = Column(Boolean,default = False)
    is_active = Column(Boolean,default = False)
    orders = relationship('Orders', back_populates='user')




# class OrderStatusEnum(str, Enum):
#     PENDING = 'pending'
#     IN_TRANSIT = 'in-transit'
#     DELIVERED = 'delivered'

# class PizzaSizeEnum(str, Enum):
#     SMALL = 'small'
#     MEDIUM = 'medium'
#     LARGE = 'large'
#     X_LARGE = 'x-large'

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(String, nullable=False, default='PENDING')
    pizza_size = Column(String, nullable=False, default='MEDIUM')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='orders')
