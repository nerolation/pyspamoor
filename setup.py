from setuptools import setup, find_packages

setup(
    name="py_spamoor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "web3>=6.15.1",
        "eth-account>=0.10.0",
        "eth-typing>=3.5.2",
        "eth-utils>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=6.0.0",
            "sphinx_rtd_theme>=1.2.0",
        ],
    },
    description="Ethereum transaction management tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Spamoor",
    author_email="author@example.com",
    url="https://github.com/yourusername/py_spamoor",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ethereum, blockchain, wallet, transactions",
    python_requires=">=3.8",
)
