from pydantic import BaseModel
from typing import Dict, Any

class PowRequest(BaseModel):
    base: float
    exponent: float

class FibonacciRequest(BaseModel):
    n: int

class FactorialRequest(BaseModel):
    n: int

class MathResponse(BaseModel):
    operation: str
    input: Dict[str, Any]
    result: Any

