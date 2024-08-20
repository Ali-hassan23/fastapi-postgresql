from fastapi import FastAPI

from routes.auth_routes import auth_router
from routes.order_routes import order_router
from db import Base,engine
import models


app = FastAPI()

models.Base.metadata.create_all(bind = engine)

app.include_router(auth_router)
app.include_router(order_router)
