import asyncio

from ..retrial.retry import retry


class ExampleException(Exception):
    pass


def retry_for_result(result):
    return result == 9


def retry_for_exception(exception):
    return isinstance(exception, ExampleException)


@retry(retry_for_result=retry_for_result)
def check_result(arg1, arg2):
    yield from asyncio.sleep(2)
    return arg1 + arg2


@retry(retry_for_exception=retry_for_exception)
def check_exception():
    yield from asyncio.sleep(2)
    raise Exception('Dummy exception thrown')


@retry(timeout=2)
def check_timeout():
    yield from asyncio.sleep(5)
    return


if __name__ == '__main__':
    asyncio.async(check_timeout())
    asyncio.get_event_loop().run_forever()
