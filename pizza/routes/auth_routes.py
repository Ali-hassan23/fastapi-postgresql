from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Union, Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta, datetime,timezone

from schemas.UserSchema import UserSignUp, ViewUser, UserLogin, TokenData, Token
from models import User
from db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

auth_router = APIRouter(prefix='/auth', tags=["Authentication"])

SECRET_KEY = "e4b53de17f381c49ef0568b934ee5e8dab33954e91e3e2b79df7cc2e7d9e4e35"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain, hash):
    return pwd_context.verify(plain, hash)

def hash_password(password):
    return pwd_context.hash(password)

def get_user(db:Session ,username: str):
    req_user = db.query(User).filter(User.username == username.lower()).first()
    if req_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    else:
        return req_user
    

def authenticate_user(db:Session ,username: str, password: str):
    user = get_user(db,username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db,username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_router.get("/", response_model=ViewUser)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@auth_router.post('/signup', response_model=ViewUser, status_code=status.HTTP_201_CREATED)
def signup(user: UserSignUp, db: Session = Depends(get_db)):
    new_user = User(
        username=user.username.lower().replace(" ", ""),
        email=user.email,
        password=hash_password(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        if "duplicate key value violates unique constraint" in str(e.orig):
            if "DETAIL:  Key (email)" in str(e.orig):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with same email already exists")
            elif "DETAIL:  Key (username)" in str(e.orig):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with same username already exists")


def get_active_staff(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_staff:
        return current_user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")




