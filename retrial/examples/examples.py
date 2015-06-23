import asyncio

from ..retrial.retry import retry


def retry_for_result(result):
    return result == 9

def retry_for_exception():
    return False

@retry(retry_for_result, retry_for_exception)
def func_to_retry(arg1, arg2):
    yield from asyncio.sleep(2)
    return arg1 + arg2

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(func_to_retry(4, 5))

