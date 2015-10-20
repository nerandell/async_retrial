from setuptools import setup, find_packages

setup(name='async_retrial',
      version='0.7',
      author='Ankit Chandawala',
      author_email='ankitchandawala@gmail.com',
      url='https://github.com/nerandell/async_retrial',
      description='asyncio retrial library',
      packages=find_packages(exclude=['retrial.examples', 'tests']),
      zip_safe=False)
