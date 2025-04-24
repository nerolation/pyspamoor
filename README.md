# py_spamoor

[![PyPI version](https://badge.fury.io/py/py-spamoor.svg)](https://badge.fury.io/py/py-spamoor)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-spamoor.svg)](https://pypi.org/project/py-spamoor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Ethereum wallet and transaction management library designed to be slim, robust, and easy to use.

## Features

- **Ethereum Wallet Management**: Create, store, and manage Ethereum wallets
- **Transaction Building**: Build and sign Ethereum transactions with ease
- **Rate Limiting**: Control your API usage with built-in rate limiting
- **Multi-client Support**: Connect to multiple Ethereum nodes with a unified interface
- **Wallet Pooling**: Manage multiple wallets with different selection strategies

## Installation

```bash
pip install py-spamoor
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
print(f"Wallet address: {wallet.get_address()}")

# Create client configuration
client_config = ClientConfig(
    url="http://localhost:8545",  # Your Ethereum node RPC URL
    name="local_node",
    group="development"
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

# Send the transaction (if connected to a node)
tx_hash = client.send_raw_transaction(signed_tx)
print(f"Transaction sent: {tx_hash}")
```

## Documentation

For detailed documentation, see the [docs](./docs) directory or visit our [documentation website](#).

### Examples

Check out the [examples](./examples) directory for more usage examples:

```bash
cd examples
python basic_wallet.py
```

## Development

### Requirements

- Python 3.8+
- web3.py 6.15.1+
- eth-account 0.10.0+

### Testing

Run the simple test to verify your installation:

```bash
python simple_test.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 