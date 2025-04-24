# Wallet Module

The `Wallet` class is the core component for managing Ethereum wallets and signing transactions.

## Class: Wallet

```python
from py_spamoor import Wallet
```

### Constructor

```python
Wallet(private_key=None)
```

Creates a new wallet instance.

**Parameters:**
- `private_key` (str, optional): The private key for the wallet. If not provided, a random wallet will be generated.

**Examples:**

```python
# Create a new random wallet
wallet = Wallet()

# Create a wallet from an existing private key
wallet = Wallet("0x0000000000000000000000000000000000000000000000000000000000000001")
```

### Methods

#### `get_address()`

Returns the Ethereum address associated with this wallet.

**Returns:**
- `str`: The Ethereum address in checksum format.

**Example:**

```python
wallet = Wallet()
address = wallet.get_address()
print(f"Wallet address: {address}")  # e.g., 0x5Bc4D265F03D4A2Bb561da4Ac207115b392D668F
```

#### `build_transaction(to, value=0, data=None, gas=21000, gas_price=None, max_fee_per_gas=None, max_priority_fee_per_gas=None, nonce=None)`

Builds an Ethereum transaction.

**Parameters:**
- `to` (str): The recipient address.
- `value` (int, optional): The amount of Ether to send in wei. Default is 0.
- `data` (str, optional): The transaction data. Default is None.
- `gas` (int, optional): The gas limit. Default is 21000.
- `gas_price` (int, optional): The gas price in wei (for legacy transactions). Default is None.
- `max_fee_per_gas` (int, optional): The maximum fee per gas in wei (for EIP-1559 transactions). Default is None.
- `max_priority_fee_per_gas` (int, optional): The maximum priority fee per gas in wei (for EIP-1559 transactions). Default is None.
- `nonce` (int, optional): The transaction nonce. If None, it will be fetched from the network. Default is None.

**Returns:**
- `dict`: The transaction parameters.

**Example:**

```python
tx_params = wallet.build_transaction(
    to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    value=1000000000000000000,  # 1 ETH
    gas=21000,
    max_fee_per_gas=2000000000,  # 2 Gwei
    max_priority_fee_per_gas=1000000000  # 1 Gwei
)
```

#### `sign_transaction(transaction_dict)`

Signs a transaction with this wallet's private key.

**Parameters:**
- `transaction_dict` (dict): The transaction parameters, typically created with `build_transaction()`.

**Returns:**
- `str`: The signed transaction data as a hexadecimal string.

**Example:**

```python
tx_params = wallet.build_transaction(to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e", value=1000000000000000000)
signed_tx = wallet.sign_transaction(tx_params)
``` 