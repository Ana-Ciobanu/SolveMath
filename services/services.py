from sqlalchemy.orm import Session
from models.models import MathRequest

def calculate_pow(base: float, exponent: float) -> float:
    return pow(base, exponent)

def calculate_fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def calculate_factorial(n: int) -> int:
    if n < 0:
        raise ValueError("n must be >= 0")
    result = 1
    for i in range(2, n+1):
        result *= i
    return result

def persist_request(db: Session, operation: str, param1, param2, result):
    req = MathRequest(operation=operation, param1=param1, param2=param2, result=str(result))
    db.add(req)
    db.commit()