import logging
from sqlalchemy.orm import Session
from models.models import MathRequest
from fastapi_cache.decorator import cache
import redis

logger = logging.getLogger(__name__)

# Create a Redis client
redis_client = redis.Redis(host="redis", port=6379, db=0)


@cache(expire=3600)  # Cache for 1 hour
async def calculate_pow(base: float, exponent: float) -> float:
    try:
        logger.info(f"Calculating pow({base}, {exponent})")
        return pow(base, exponent)
    except Exception as e:
        logger.error(f"Error in calculate_pow: {e}")
        raise


@cache(expire=3600)
async def calculate_fibonacci(n: int) -> int:
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


@cache(expire=3600)
async def calculate_factorial(n: int) -> int:
    try:
        logger.info(f"Calculating factorial({n})")
        if n < 0:
            logger.error("n must be >= 0 for factorial")
            raise ValueError("n must be >= 0")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    except Exception as e:
        logger.error(f"Error in calculate_factorial: {e}")
        raise


def persist_request(db: Session, operation: str, param1, param2, result, username):
    try:
        req = MathRequest(
            operation=operation,
            param1=param1,
            param2=param2,
            result=str(result),
            username=username,
        )
        db.add(req)
        db.commit()
        logger.info(
            f"Persisted request: {operation} by {username} "
            f"params: {param1}, {param2}, result: {result}"
        )
    except Exception as e:
        logger.error(f"Error persisting request: {e}")
        db.rollback()
    # Redis Streams integration
    try:
        redis_client.xadd(
            "math_requests",
            {
                "operation": str(operation),
                "param1": str(param1) if param1 is not None else "",
                "param2": str(param2) if param2 is not None else "",
                "result": str(result),
                "username": str(username),
            },
        )
        logger.info("Request also sent to Redis Stream 'math_requests'")
    except Exception as re:
        logger.error(f"Failed to send request to Redis Stream: {re}")
