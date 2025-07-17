from pydantic import BaseModel

class PowRequest(BaseModel):
    base: float
    exponent: float

class FibonacciRequest(BaseModel):
    n: int

class FactorialRequest(BaseModel):
    n: int

