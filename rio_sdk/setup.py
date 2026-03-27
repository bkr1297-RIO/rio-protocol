"""
RIO SDK — Package Setup

Install in development mode:
    cd rio_sdk && pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="rio_sdk",
    version="0.1.0",
    description="Python SDK for the RIO Governance Protocol",
    long_description=open("../SDK_README.md").read() if __import__("os").path.exists("../SDK_README.md") else "",
    long_description_content_type="text/markdown",
    author="RIO Protocol",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28",
        "cryptography>=41.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
