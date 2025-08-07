import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import services.services as services
from unittest.mock import AsyncMock


@pytest.fixture(autouse=True)
def init_cache():
    # Initialize an in-memory cache before each test.
    FastAPICache.init(InMemoryBackend(), prefix="test")


@pytest.mark.asyncio
async def test_calculate_pow_caching(monkeypatch):
    # Get the undecorated logic
    original_logic = services.calculate_pow.__wrapped__
    spy = AsyncMock(wraps=original_logic)
    spy.__name__ = original_logic.__name__
    spy.__wrapped__ = original_logic

    # Patch the service function with a new cached spy
    monkeypatch.setattr(services, "calculate_pow", cache(expire=3600)(spy))

    # First call: logic should execute once
    result1 = await services.calculate_pow(2, 3)
    assert result1 == 8
    assert spy.await_count == 1

    # Second call with same args: cached, so count stays the same
    result2 = await services.calculate_pow(2, 3)
    assert result2 == 8
    assert spy.await_count == 1

    # Call with different args: cache miss → logic runs again
    result3 = await services.calculate_pow(3, 2)
    assert result3 == 9
    assert spy.await_count == 2


@pytest.mark.asyncio
async def test_calculate_fibonacci_caching(monkeypatch):
    original_logic = services.calculate_fibonacci.__wrapped__
    spy = AsyncMock(wraps=original_logic)
    spy.__name__ = original_logic.__name__
    spy.__wrapped__ = original_logic

    monkeypatch.setattr(services, "calculate_fibonacci", cache(expire=3600)(spy))

    # First call
    result1 = await services.calculate_fibonacci(10)
    assert result1 == 55
    assert spy.await_count == 1

    # Second call: cached
    result2 = await services.calculate_fibonacci(10)
    assert result2 == 55
    assert spy.await_count == 1

    # Different argument: cache miss
    result3 = await services.calculate_fibonacci(9)
    assert result3 == 34
    assert spy.await_count == 2


@pytest.mark.asyncio
async def test_calculate_factorial_caching(monkeypatch):
    original_logic = services.calculate_factorial.__wrapped__
    spy = AsyncMock(wraps=original_logic)
    spy.__name__ = original_logic.__name__
    spy.__wrapped__ = original_logic

    monkeypatch.setattr(services, "calculate_factorial", cache(expire=3600)(spy))

    # First call
    result1 = await services.calculate_factorial(5)
    assert result1 == 120
    assert spy.await_count == 1

    # Second call: cached
    result2 = await services.calculate_factorial(5)
    assert result2 == 120
    assert spy.await_count == 1

    # Different argument: cache miss
    result3 = await services.calculate_factorial(4)
    assert result3 == 24
    assert spy.await_count == 2
