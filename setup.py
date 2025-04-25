from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py_spamoor",
    version="0.1.0",
    author="py_spamoor Developers",
    author_email="your_email@example.com",
    description="A Python tool for Ethereum transaction automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/py_spamoor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "eth-typing>=3.0.0",
        "eth-utils>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "py_spamoor=py_spamoor.cli:main",
        ],
    },
)
