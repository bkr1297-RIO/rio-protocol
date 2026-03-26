from setuptools import setup, find_packages

setup(
    name="rio-sdk",
    version="1.0.0",
    description="RIO Protocol SDK — verify receipts, run conformance tests, check compliance level",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
