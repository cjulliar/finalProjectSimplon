from setuptools import setup, find_packages

setup(
    name="bank-reports",
    version="1.0.0",
    description="Système d'Automatisation des Rapports Bancaires",
    author="Simplon",
    author_email="contact@simplon.co",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
        "sqlalchemy>=2.0.20",
        "pandas>=2.1.0",
        "openpyxl>=3.1.2",
        "python-jose>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.6",
        "pytest>=7.4.0",
        "httpx>=0.24.1",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
) 