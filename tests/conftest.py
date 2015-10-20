import pytest

from retrial.retrial.retry import RetryHandler

@pytest.fixture
def exponential_retry_handler():
    return RetryHandler(multiplier=2)

@pytest.fixture
def strategic_retry_handler():
    return RetryHandler(strategy=[0, 3, 7, 11])
