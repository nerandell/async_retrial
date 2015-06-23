from functools import wraps
import asyncio
from concurrent.futures import TimeoutError
from .log import logger


def _default_retry_for_result(result):
    return False


def _default_retry_for_exception(exception):
    return False


def retry(*dargs, **dkwargs):
    if len(dargs) == 1 and callable(dargs[0]):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                yield from RetryHandler().run(func, *args, **kwargs)
            return wrapper
        return decorator(dargs[0])

    else:
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                yield from RetryHandler(*dargs, **dkwargs).run(func, *args, **kwargs)
            return wrapper

        return decorator


class RetryHandler:
    def __init__(self, should_retry_for_result=_default_retry_for_result,
                 should_retry_for_exception=_default_retry_for_exception,
                 multiplier=2, timeout=None):
        self._should_retry_for_result = should_retry_for_result
        self._should_retry_for_exception = should_retry_for_exception
        self._multiplier = multiplier
        self._timeout = timeout

    @asyncio.coroutine
    def run(self, func, *args, **kwargs):
        attempt_made = 0
        if not asyncio.iscoroutinefunction(func):
            func = asyncio.coroutine(func)
        yield from self._run_task(attempt_made, func, *args, **kwargs)

    @asyncio.coroutine
    def _run_task(self, attempts_made, func, *args, **kwargs):
        wait_time = self._multiplier ** attempts_made
        logger.info('Retrying %s after %s seconds', func.__name__, wait_time)
        yield from asyncio.sleep(wait_time)
        try:
            if self._timeout is None:
                result = yield from func(*args, **kwargs)
            else:
                try:
                    result = yield from asyncio.wait_for(func(*args, **kwargs), self._timeout)
                except TimeoutError:
                    yield from self._run_task(attempts_made + 1, func, *args, **kwargs)
                    return
            logger.info('Result retrieved from %s is %s', func.__name__, result)
            if self._should_retry_for_result(result):
                yield from self._run_task(attempts_made + 1, func, *args, **kwargs)

        except Exception as e:
            logger.info('%s raised exception %s', func.__name__, e.__class__.__name__)
            if self._should_retry_for_exception(e):
                yield from self._run_task(attempts_made + 1, func, *args, **kwargs)
