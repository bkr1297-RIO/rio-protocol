"""
RIO Protocol — Setup Script
Allows installation via: pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="rio-protocol",
    version="1.0.0",
    author="Brian K. Rasmussen",
    description="RIO — Runtime Intelligence Orchestration: Fail-closed execution governance with cryptographic audit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bkr1297-RIO/rio-protocol",
    packages=find_packages(exclude=["tests*", "whitepaper*", "examples*"]),
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rio-init=scripts.init_rio:main",
            "rio-run=scripts.run_all:main",
            "rio-admin=scripts.create_admin_user:main",
            "rio-test=runtime.test_harness:run_all_tests",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="governance, audit, compliance, ai-safety, execution-control, cryptographic-receipts",
)
