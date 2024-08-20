from pydantic import BaseModel
from typing import Optional

class UserSignUp(BaseModel):
    username : str
    email : str
    password : str
    is_staff : Optional[bool]
    is_active : Optional[bool]


class ViewUser(BaseModel):
    id : Optional[int]
    username : str
    email : str
    password : str
    is_staff : Optional[bool]
    is_active : Optional[bool]


class UserLogin(BaseModel):
    username : str
    password : str

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : str

class UserInDb(BaseModel):
    hashed_password : str
