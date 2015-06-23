from functools import wraps
import asyncio

from .log import logger

def retry(should_retry_for_result, should_retry_for_exception, multiplier=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            yield from RetryHandler(should_retry_for_result, should_retry_for_exception, multiplier).run(func, *args,
                                                                                                         **kwargs)
        return wrapper
    return decorator

class RetryHandler:
    def __init__(self, should_retry_for_result, should_retry_for_exception, multiplier=2):
        self._should_retry_for_result = should_retry_for_result
        self._should_retry_for_exception = should_retry_for_exception
        self._multiplier = multiplier

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
            result = yield from func(*args, **kwargs)
            logger.info('Result retrieved from %s is %s', func.__name__, result)
            if self._should_retry_for_result(result):
                yield from self._run_task(attempts_made + 1, func, *args, **kwargs)

        except Exception as e:
            logger.info('Debugging %s because it raised exception %s', func.__name__, str(e))
            if self._should_retry_for_exception(e):
                yield from self._run_task(attempts_made + 1, func, *args, **kwargs)
