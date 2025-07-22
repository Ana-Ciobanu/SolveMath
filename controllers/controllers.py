from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from schemas.schemas import PowRequest, FibonacciRequest, FactorialRequest, MathResponse
from services.services import calculate_pow, calculate_fibonacci, calculate_factorial, persist_request
from db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from models.models import User
from schemas.schemas import UserCreate
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/pow", response_model=MathResponse)
async def pow_endpoint(request: PowRequest, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    result = await calculate_pow(request.base, request.exponent)
    persist_request(db, "pow", request.base, request.exponent, result)
    return MathResponse(operation="pow", input={"base": request.base, "exponent": request.exponent}, result=result)

@router.post("/fibonacci", response_model=MathResponse)
async def fibonacci_endpoint(request: FibonacciRequest, db: Session = Depends(get_db),token: dict = Depends(verify_token)):
    result = await calculate_fibonacci(request.n)
    persist_request(db, "fibonacci", request.n, None, result)
    return MathResponse(operation="fibonacci", input={"n": request.n}, result=result)

@router.post("/factorial", response_model=MathResponse)
async def factorial_endpoint(request: FactorialRequest, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    result = await calculate_factorial(request.n)
    persist_request(db, "factorial", request.n, None, result)
    return MathResponse(operation="factorial", input={"n": request.n}, result=result)