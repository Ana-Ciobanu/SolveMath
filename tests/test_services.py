import pytest
from services.services import calculate_pow, calculate_fibonacci, calculate_factorial
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


@pytest.fixture(scope="session", autouse=True)
def init_cache():
    FastAPICache.init(InMemoryBackend())


@pytest.mark.asyncio
async def test_calculate_pow():
    assert await calculate_pow(2, 3) == 8
    assert await calculate_pow(10, 0) == 1
    assert await calculate_pow(-2, 2) == 4


@pytest.mark.asyncio
async def test_calculate_fibonacci():
    assert await calculate_fibonacci(0) == 0
    assert await calculate_fibonacci(1) == 1
    assert await calculate_fibonacci(10) == 55


@pytest.mark.asyncio
async def test_calculate_factorial():
    assert await calculate_factorial(0) == 1
    assert await calculate_factorial(5) == 120
    assert await calculate_factorial(10) == 3628800


@pytest.mark.asyncio
async def test_calculate_fibonacci_negative():
    with pytest.raises(ValueError, match="n must be >= 0"):
        await calculate_fibonacci(-1)


@pytest.mark.asyncio
async def test_calculate_factorial_negative():
    with pytest.raises(ValueError, match="n must be >= 0"):
        await calculate_factorial(-5)
