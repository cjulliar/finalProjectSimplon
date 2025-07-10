from setuptools import setup, find_packages

# Lire le README.md s'il existe, sinon utiliser une description par défaut
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Système d'analyse et de génération de rapports bancaires"

# Lire requirements.txt s'il existe, sinon utiliser une liste vide
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = []

setup(
    name="bank-reports-system",
    version="1.0.0",
    author="Cyril Julliard",
    author_email="cyril.julliard@example.com",
    description="Système d'analyse et de génération de rapports bancaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyriljulliard/bank-reports-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bank-reports=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
) 