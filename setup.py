from setuptools import setup, find_packages

setup(
    name="bankreports",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "sqlalchemy",
        "openpyxl",
    ],
) 