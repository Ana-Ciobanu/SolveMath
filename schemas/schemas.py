from pydantic import BaseModel, Field
from typing import Dict, Any


class PowRequest(BaseModel):
    base: float = Field(..., ge=-1e6, le=1e6)
    exponent: float = Field(..., ge=-1000, le=1000)


class FibonacciRequest(BaseModel):
    n: int = Field(..., ge=0, le=20000)


class FactorialRequest(BaseModel):
    n: int = Field(..., ge=0, le=1550)


class MathResponse(BaseModel):
    operation: str
    input: Dict[str, Any]
    result: Any


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
