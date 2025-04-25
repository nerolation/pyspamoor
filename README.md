# py_spamoor

A Python tool for Ethereum transaction automation.

## Features

- ETH transfers
- ERC20 token approvals
- Custom contract function calls
- Transaction batching and retry logic
- Multi-wallet and multi-RPC support

## Installation

```bash
git clone https://github.com/yourusername/py_spamoor.git
cd py_spamoor
pip install -e .
```

## Usage

### Basic Usage

```bash
python -m py_spamoor --private-key YOUR_PRIVATE_KEY --rpc https://ethereum-rpc.com
```

### Modes

#### Read-Only Mode (Default)

```bash
python -m py_spamoor --private-key YOUR_PRIVATE_KEY --rpc https://ethereum-rpc.com --mode read_only
```

#### ETH Transfer

```bash
python -m py_spamoor --private-key YOUR_PRIVATE_KEY --rpc https://ethereum-rpc.com --mode eth_transfer --recipient 0xRecipientAddress --amount 0.01
```

#### Token Approval

```bash
python -m py_spamoor --private-key YOUR_PRIVATE_KEY --rpc https://ethereum-rpc.com --mode token_approval --token-address 0xTokenAddress --spender 0xSpenderAddress
```

#### Custom Function

```bash
python -m py_spamoor --private-key YOUR_PRIVATE_KEY --rpc https://ethereum-rpc.com --mode custom_function --contract-address 0xContractAddress --contract-abi /path/to/abi.json --function-name myFunction --function-args arg1 arg2
```

### Advanced Options

- `--max-concurrent`: Maximum number of concurrent transactions (default: 1)
- `--tx-count`: Number of transactions to execute (default: 1)
- `--min-delay`: Minimum delay between transactions in seconds (default: 0.5)
- `--max-delay`: Maximum delay between transactions in seconds (default: 3.0)
- `--gas-price`: Manual gas price setting (in wei)
- `--chain-id`: Manual chain ID setting
- `--verbose`: Enable verbose output
- `--output`: Path to write JSON output

### Using Key Files

Instead of passing private keys directly, you can use a file:

```bash
echo "your_private_key" > keys.txt
python -m py_spamoor --private-key keys.txt --rpc https://ethereum-rpc.com
```

### Using Multiple RPC Endpoints

```bash
echo "https://rpc1.com" > rpcs.txt
echo "https://rpc2.com" >> rpcs.txt
python -m py_spamoor --private-key YOUR_PRIVATE_KEY --rpc rpcs.txt
```

## Examples

### Perform 5 ETH Transfers

```bash
python -m py_spamoor --private-key keys.txt --rpc https://ethereum-rpc.com --mode eth_transfer --recipient 0xRecipientAddress --amount 0.001 --tx-count 5
```

### Approve a Token with Maximum Amount

```bash
python -m py_spamoor --private-key keys.txt --rpc https://ethereum-rpc.com --mode token_approval --token-address 0xTokenAddress --spender 0xSpenderAddress --approval-amount unlimited
```

### Run Multiple Concurrent Transactions

```bash
python -m py_spamoor --private-key keys.txt --rpc https://ethereum-rpc.com --mode eth_transfer --recipient 0xRecipientAddress --amount 0.001 --tx-count 10 --max-concurrent 3
```

## License

MIT 

## CLI Usage

The `py_spamoor` package comes with a powerful command-line interface for spamming Ethereum transactions using different strategies.

### Quick Start

```bash
# Install the package
pip install -e .

# Run with default settings (requires pks.txt and rpc.txt files)
python -m py_spamoor --chain-id 3151908

# Run with custom file paths
python -m py_spamoor --private-keys-file my_keys.txt --rpc-file my_rpc.txt --chain-id 1
```

### Example Files

#### Private Keys File (pks.txt)
```json
[
  {"private_key": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"},
  {"private_key": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"}
]
```

#### RPC Endpoints File (rpc.txt)
```
el-1-geth   rpc: 8545/tcp -> 127.0.0.1:10545
el-2-nethermind   rpc: 8545/tcp -> 127.0.0.1:10546
```

### Available Options

```
usage: __main__.py [-h] [--private-keys-file PRIVATE_KEYS_FILE] [--rpc-file RPC_FILE] [--chain-id CHAIN_ID]
                   [--wallet-selection {index,random,round-robin}] [--client-selection {index,random,round-robin}]
                   [--strategy-selection {index,random,round-robin}] [--strategies STRATEGIES] [--gas-limit GAS_LIMIT]
                   [--max-fee-per-gas MAX_FEE_PER_GAS] [--max-priority-fee-per-gas MAX_PRIORITY_FEE_PER_GAS]
                   [--max-fee-per-blob-gas MAX_FEE_PER_BLOB_GAS] [--tx-delay TX_DELAY] [--tx-count TX_COUNT] [--verbose]
                   [--dry-run]

Ethereum Transaction Spammer

options:
  -h, --help            show this help message and exit
  --private-keys-file PRIVATE_KEYS_FILE, -k PRIVATE_KEYS_FILE
                        Path to file containing private keys (default: pks.txt)
  --rpc-file RPC_FILE, -r RPC_FILE
                        Path to file containing RPC endpoints (default: rpc.txt)
  --chain-id CHAIN_ID, -c CHAIN_ID
                        Chain ID for transactions (default: 3151908)
  --wallet-selection {index,random,round-robin}, -w {index,random,round-robin}
                        Wallet selection mode (default: round-robin)
  --client-selection {index,random,round-robin}, -n {index,random,round-robin}
                        Client selection mode (default: round-robin)
  --strategy-selection {index,random,round-robin}, -s {index,random,round-robin}
                        Strategy selection mode (default: round-robin)
  --strategies STRATEGIES
                        Transaction strategies to use (comma-separated) (default: standard-tx,calldata-zeros)
  --gas-limit GAS_LIMIT
                        Gas limit for transactions (will use block limit if not specified) (default: None)
  --max-fee-per-gas MAX_FEE_PER_GAS
                        Max fee per gas (wei) (default: 1000000000)
  --max-priority-fee-per-gas MAX_PRIORITY_FEE_PER_GAS
                        Max priority fee per gas (wei) (default: 1000000000)
  --max-fee-per-blob-gas MAX_FEE_PER_BLOB_GAS
                        Max fee per blob gas (wei, for blob transactions) (default: 1000000000)
  --tx-delay TX_DELAY   Delay between transactions (seconds) (default: 1.0)
  --tx-count TX_COUNT   Number of transactions to send (0 for unlimited) (default: 0)
  --verbose, -v         Increase output verbosity (default: False)
  --dry-run             Don't send transactions, just print them (default: False)
```

### Available Transaction Strategies

- `standard-tx`: Simple ETH transfer transactions
- `calldata-zeros`: Transactions with maximum zero-byte calldata
- `calldata-non-zeros`: Transactions with maximum non-zero-byte calldata
- `calldata-mix`: Transactions with a mix of zero and non-zero calldata
- `access-list`: Transactions with EIP-2930 access lists
- `blobs`: EIP-4844 blob transactions

### Example Commands

```bash
# Dry run with standard transactions 
python -m py_spamoor --chain-id 3151908 --strategies standard-tx --dry-run

# Send 10 transactions with mixed calldata
python -m py_spamoor --chain-id 3151908 --strategies calldata-mix --tx-count 10

# Use only blob transactions with a higher blob gas fee
python -m py_spamoor --chain-id 3151908 --strategies blobs --max-fee-per-blob-gas 2000000000

# Use multiple strategies in round-robin mode
python -m py_spamoor --chain-id 3151908 --strategies standard-tx,calldata-zeros,access-list

# Send transactions faster with a shorter delay
python -m py_spamoor --chain-id 3151908 --tx-delay 0.1
```

### Programmatic Usage Example

You can also use the core components programmatically:

```python
from py_spamoor import Wallet, WalletPool, WalletSelectionMode, Client, ClientConfig, ClientSelectionMode
from py_spamoor.wallet_pool import Strategy, StrategySelectionMode
from py_spamoor.helper import load_private_keys, parse_el_rpc_endpoints, get_max_calldata_zeros_for_limit, generate_zero_bytes

# Initialize wallet pool
pool = WalletPool()
pool.load_private_key_from_file("pks.txt")
pool.load_clients_from_file("rpc.txt")
pool.add_strategy([Strategy.STANDARD_TX, Strategy.CALLDATA_ZEROS])

# Setup generators
clients_gen = lambda: pool.get_client(ClientSelectionMode.ROUND_ROBIN)
wallet_gen = lambda: pool.get_wallet(WalletSelectionMode.ROUND_ROBIN)
strategies_gen = lambda: pool.get_strategy(StrategySelectionMode.ROUND_ROBIN)

# Main loop
while True:
    print("-----------")
    client, wallet, strategy = clients_gen(), wallet_gen(), strategies_gen()
    
    if strategy == Strategy.STANDARD_TX:
        tx = wallet.build_transaction(wallet.get_address(), chain_id=3151908)
        
    elif strategy == Strategy.CALLDATA_ZEROS:
        block_gas_limit = client.block_gas_limit
        calldata_zeros = get_max_calldata_zeros_for_limit(block_gas_limit)
        data = generate_zero_bytes(calldata_zeros)
        tx = wallet.build_transaction(
            wallet.get_address(), 
            chain_id=3151908,
            gas=block_gas_limit,
            data=data
        )
    else:
        print("skip")
        continue
        
    signed_tx = wallet.sign_transaction(tx, client)
    tx_hash = client.send_transaction(signed_tx)
    print(client.wait_for_transaction_receipt(tx_hash))
    time.sleep(1) 