from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from schemas.schemas import PowRequest, FibonacciRequest, FactorialRequest, MathResponse
from services.services import calculate_pow, calculate_fibonacci
from services.services import calculate_factorial, persist_request
from db.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, UTC, timedelta
from models.models import User, MathRequest, LogEntry
from schemas.schemas import UserCreate
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import logging

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


logger = logging.getLogger(__name__)

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Prevent registration with username 'admin'
    if user.username.lower() == "admin":
        logger.error("Attempted registration with reserved username 'admin'")
        raise HTTPException(
            status_code=400, detail="Registration with username 'admin' is not allowed"
        )

    # Check if user exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logger.error(
            f"Attempted registration with already registered username '{user.username}'"
        )
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw, role="user")
    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.error(f"Failed login attempt for username '{form_data.username}'")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    # Set HTTP-only cookie
    response = Response(
        content='{"message": "Login successful"}', media_type="application/json"
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=os.getenv("HTTP_SECURE") == "True",
        samesite="lax",
        max_age=60 * 60 * 24,
    )
    return response


@router.post("/logout")
def logout(response: Response):
    response = Response(
        content='{"message": "Logged out"}', media_type="application/json"
    )
    response.delete_cookie("access_token")
    return response


@router.get("/me")
def get_current_user(token: dict = Depends(get_token_from_cookie)):
    return {"username": token["sub"], "role": token["role"]}


@router.post("/pow", response_model=MathResponse)
async def pow_endpoint(
    request: PowRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(get_token_from_cookie),
    background_tasks: BackgroundTasks = None,
):
    result = await calculate_pow(request.base, request.exponent)
    background_tasks.add_task(
        persist_request, db, "pow", request.base, request.exponent, result, token["sub"]
    )
    return MathResponse(
        operation="pow",
        input={"base": request.base, "exponent": request.exponent},
        result=result,
    )


@router.post("/fibonacci", response_model=MathResponse)
async def fibonacci_endpoint(
    request: FibonacciRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(get_token_from_cookie),
    background_tasks: BackgroundTasks = None,
):
    result = await calculate_fibonacci(request.n)
    background_tasks.add_task(
        persist_request, db, "fibonacci", request.n, None, result, token["sub"]
    )
    return MathResponse(operation="fibonacci", input={"n": request.n}, result=result)


@router.post("/factorial", response_model=MathResponse)
async def factorial_endpoint(
    request: FactorialRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(get_token_from_cookie),
    background_tasks: BackgroundTasks = None,
):
    result = await calculate_factorial(request.n)
    background_tasks.add_task(
        persist_request, db, "factorial", request.n, None, result, token["sub"]
    )
    return MathResponse(operation="factorial", input={"n": request.n}, result=result)


@router.get("/admin/requests")
def get_math_requests(
    db: Session = Depends(get_db), token: dict = Depends(get_token_from_cookie)
):
    if token.get("role") != "admin":
        logger.error("Unauthorized access attempt to /admin/requests")
        raise HTTPException(status_code=403, detail="Admin access required")
    requests = (
        db.query(MathRequest).order_by(MathRequest.timestamp.desc()).limit(100).all()
    )
    return [
        {
            "id": r.id,
            "operation": r.operation,
            "param1": r.param1,
            "param2": r.param2,
            "result": r.result,
            "timestamp": r.timestamp.isoformat(),
            "username": r.username,
        }
        for r in requests
    ]


@router.get("/admin/logs")
def get_log_entries(
    db: Session = Depends(get_db), token: dict = Depends(get_token_from_cookie)
):
    if token.get("role") != "admin":
        logger.error("Unauthorized access attempt to /admin/logs")
        raise HTTPException(status_code=403, detail="Admin access required")
    logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(100).all()
    return [
        {
            "id": log_entry.id,
            "level": log_entry.level,
            "message": log_entry.message,
            "timestamp": log_entry.timestamp.isoformat(),
        }
        for log_entry in logs
    ]
