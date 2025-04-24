# py_spamoor Documentation

Welcome to the py_spamoor documentation. This library provides lightweight Ethereum wallet and transaction management tools.

## Overview

py_spamoor is designed to simplify Ethereum wallet management, transaction creation, and interaction with Ethereum nodes.
It provides a clean, intuitive API for blockchain developers who need reliable tools without unnecessary complexity.

## Features

- **Wallet Management**: Create, store, and manage Ethereum wallets
- **Transaction Building**: Build and sign Ethereum transactions with ease
- **Rate Limiting**: Control your API usage with built-in rate limiting
- **Multi-client Support**: Connect to multiple Ethereum nodes with a unified interface
- **Wallet Pooling**: Manage multiple wallets with different selection strategies

## Installation

```bash
pip install py_spamoor
```

Or from source:

```bash
git clone https://github.com/yourusername/py_spamoor
cd py_spamoor
pip install -e .
```

## Quick Start

```python
from py_spamoor import Wallet, ClientConfig, Client

# Create a wallet
wallet = Wallet()  # Generates a new wallet
# or load from private key
wallet = Wallet("0x0000000000000000000000000000000000000000000000000000000000000001")

# Create client configuration
client_config = ClientConfig(
    url="https://ethereum-rpc-endpoint.example.com",
    name="main_node",
    group="production"
)

# Initialize client
client = Client(client_config)

# Build a transaction
tx_params = wallet.build_transaction(
    to="0xffffffffffffffffffffffffffffffffffffffff",
    value=1000000000000000,  # 0.001 ETH in wei
    gas=21000,
    max_fee_per_gas=2000000000,  # 2 Gwei
    max_priority_fee_per_gas=1000000000  # 1 Gwei
)

# Sign the transaction
signed_tx = wallet.sign_transaction(tx_params)

# Send the transaction
tx_hash = client.send_raw_transaction(signed_tx)
print(f"Transaction sent: {tx_hash}")
```

## API Reference

For detailed documentation on all modules and classes, see the [API Reference](api/index.md).

## Examples

Check out the [examples section](examples/index.md) for more detailed usage examples.

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](contributing.md) for more information. 