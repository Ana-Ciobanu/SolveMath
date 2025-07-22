from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.schemas import PowRequest, FibonacciRequest, FactorialRequest, MathResponse
from services.services import calculate_pow, calculate_fibonacci, calculate_factorial, persist_request
from db.database import get_db

router = APIRouter()

@router.post("/pow", response_model=MathResponse)
def pow_endpoint(request: PowRequest, db: Session = Depends(get_db)):
    result = calculate_pow(request.base, request.exponent)
    persist_request(db, "pow", request.base, request.exponent, result)
    return MathResponse(operation="pow", input={"base": request.base, "exponent": request.exponent}, result=result)

@router.post("/fibonacci", response_model=MathResponse)
def fibonacci_endpoint(request: FibonacciRequest, db: Session = Depends(get_db)):
    result = calculate_fibonacci(request.n)
    persist_request(db, "fibonacci", request.n, None, result)
    return MathResponse(operation="fibonacci", input={"n": request.n}, result=result)

@router.post("/factorial", response_model=MathResponse)
def factorial_endpoint(request: FactorialRequest, db: Session = Depends(get_db)):
    result = calculate_factorial(request.n)
    persist_request(db, "factorial", request.n, None, result)
    return MathResponse(operation="factorial", input={"n": request.n}, result=result)
