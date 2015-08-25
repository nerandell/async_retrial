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
                 multiplier=2, timeout=None, max_attempts=None, strategy=None):
        self._should_retry_for_result = should_retry_for_result
        self._should_retry_for_exception = should_retry_for_exception
        self._multiplier = multiplier
        self._timeout = timeout
        self._max_attempts = max_attempts
        self._strategy = strategy

    @asyncio.coroutine
    def run(self, func, *args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            func = asyncio.coroutine(func)
        return (yield from self._run_task(0, func, *args, **kwargs))

    @asyncio.coroutine
    def _run_task(self, attempts_made, func, *args, **kwargs):
        if self._max_attempts is not None and attempts_made > self._max_attempts:
            return
        wait_time = self._get_wait_time(attempts_made)
        logger.info('Retrying %s after %s seconds', func.__name__, wait_time)
        yield from asyncio.sleep(wait_time)
        try:
            if self._timeout is None:
                result = yield from func(*args, **kwargs)
            else:
                try:
                    result = yield from asyncio.wait_for(func(*args, **kwargs), self._timeout)
                except TimeoutError:
                    return (yield from self._run_task(attempts_made + 1, func, *args, **kwargs))
            logger.info('Result retrieved from %s is %s', func.__name__, result)
            if self._should_retry_for_result(result):
                return (yield from self._run_task(attempts_made + 1, func, *args, **kwargs))
            else:
                return result

        except Exception as e:
            logger.exception('%s raised exception %s', func.__name__, e.__class__.__name__)
            if self._should_retry_for_exception(e):
                yield from self._run_task(attempts_made + 1, func, *args, **kwargs)
            else:
                raise

    def _get_wait_time(self, attempts_made):
        if self._strategy:
            return self._strategy[min(attempts_made, len(self._strategy)-1)]
        else:
            return self._multiplier ** attempts_made if attempts_made != 0 else 0

