Retrial library for asyncio coroutines
======================================
.. image:: https://travis-ci.org/nerandell/async_retrial.svg?branch=master
    :target: https://travis-ci.org/nerandell/async_retrial

Easy to use retry library based on asyncio_

.. _asyncio: https://docs.python.org/3/library/asyncio.html

Requirements
------------
- Python >= 3.3
- asyncio https://pypi.python.org/pypi/asyncio

Installation
------------

To install via pip

.. code-block:: bash

    $ pip install async_retrial
    
To install from source

.. code-block:: bash

    $ git clone https://github.com/nerandell/async_retrial
    $ cd async_retrial
    $ python setup.py install

Examples
--------

You can either use ``RetryHandler`` or ``retry`` decorator

``retry`` decorator

.. code-block:: python

    def retry(should_retry_for_result=_default_retry_for_result, 
              should_retry_for_exception=_default_retry_for_exception,
              multiplier=2, timeout=None, max_attempts=None, strategy=None):
                """
        :param should_retry_for_result: A function that is called with argument as result to allow retrial for specific
                                        set of results. Must return a boolean value
        :param should_retry_for_exception: A function that is called if the function to be retried threw an exception 
                                           allow retrial for specific set of exceptions. Must return a boolean value
        :param multiplier: Must be an integer value, If defined, the retrial would be exponential with this behind the 
                           multiplier
        :param timeout: If defined, the function will be retried if no result was returned in this time.
        :param max_attempts: Max number of attempts to retry
        :param strategy: Must be a list of integers. If defined, retrial would follow this strategy. For ex. if strategy 
                         is [1,3,5,8,11], function would be retried at 1, 3, 5, 8, 11, 11, 11, ... seconds
        :return:
        """

To use the decorator:

.. code-block:: python

    from retrial.retrial import retry
    
Using different settings:

.. code-block:: python

    @retry()
    def my_function(*args, **kwargs):
        '''Retry till successful. Default multiplier is 2'''
        
    @retry(multiplier=3)
    def my_function(*args, **kwargs):
        '''Retry at 0, 3, 9, 27, 81 ... seconds until successful'''
        
    @retry(strategy=[1, 1, 2, 3, 5, 8, 13])
    def my_function(*args, **kwargs):
        '''Retry at 1, 1, 2, 3, 5, 8, 13, 13, 13 ... seconds until successful''' 
        
    @retry(max_attempts=3)
    def my_function(*args, **kwargs):
        '''Retry for a maximum of 3 times'''
    
    @retry(should_retry_for_result=lambda x: x < 0)
    def my_function(*args, **kwargs):
        '''Retry if result is negative value'''
    
    @retry(should_retry_for_exception=lambda x: isinstance(x, KeyError))
    def my_function(*args, **kwargs):
        '''Retry if exception was of type KeyError'''

License
-------
``async_retrial`` is offered under the MIT license.

Source code
-----------
The latest developer version is available in a github repository:
https://github.com/nerandell/async_retrial
        
