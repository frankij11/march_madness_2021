import setuptools
from setuptools import find_packages, setup

with open("requirements.txt", "r") as fh:
    depends = fh.read()


setup(
    name='march_madness_2021',
    packages=find_packages(),
    version='0.1.0',
    description='Bracketology like prediction algoirthm for 2021 NCAA Basketall Tournament',
    install_requires = depends,
    package_data={"": ['data/*']},
    author='Kevin Joy',
    license='MIT',
)
