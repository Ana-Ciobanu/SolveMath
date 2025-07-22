import logging
from sqlalchemy.orm import Session
from models.models import MathRequest

logger = logging.getLogger(__name__)

def calculate_pow(base: float, exponent: float) -> float:
    try:
        logger.info(f"Calculating pow({base}, {exponent})")
        return pow(base, exponent)
    except Exception as e:
        logger.error(f"Error in calculate_pow: {e}")
        raise

def calculate_fibonacci(n: int) -> int:
    try:
        logger.info(f"Calculating fibonacci({n})")
        if n < 0:
            logger.error("n must be >= 0 for fibonacci")
            raise ValueError("n must be >= 0")
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    except Exception as e:
        logger.error(f"Error in calculate_fibonacci: {e}")
        raise

def calculate_factorial(n: int) -> int:
    try:
        logger.info(f"Calculating factorial({n})")
        if n < 0:
            logger.error("n must be >= 0 for factorial")
            raise ValueError("n must be >= 0")
        result = 1
        for i in range(2, n+1):
            result *= i
        return result
    except Exception as e:
        logger.error(f"Error in calculate_factorial: {e}")
        raise

def persist_request(db: Session, operation: str, param1, param2, result):
    try:
        req = MathRequest(operation=operation, param1=param1, param2=param2, result=str(result))
        db.add(req)
        db.commit()
        logger.info(f"Persisted request: {operation} with params {param1}, {param2} and result {result}")
    except Exception as e:
        logger.error(f"Error persisting request: {e}")
        db.rollback()