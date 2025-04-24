#!/usr/bin/env python3

"""
Demo script showing how to use py_spamoor package.
"""

import time
from py_spamoor import Wallet, ClientConfig, Client, rate_limited, WalletPool, WalletSelectionMode, ClientSelectionMode

def main():
    print("=== py_spamoor Demo ===")
    
    # 1. Create wallet
    print("\n1. Creating wallet...")
    # This is a demo private key, DO NOT use in production
    wallet = Wallet("0x0000000000000000000000000000000000000000000000000000000000000001")
    print(f"   Wallet address: {wallet.get_address()}")
    
    # 2. Create client config
    print("\n2. Creating client configuration...")
    client_config = ClientConfig(
        url="http://localhost:8545",  # Local Ethereum node 
        name="local_node",
        group="development"
    )
    print(f"   Client name: {client_config.name}")
    print(f"   Client group: {client_config.group}")
    
    # 3. Demonstrate rate limiting
    print("\n3. Demonstrating rate limiting...")
    call_count = 0
    
    @rate_limited(calls_per_second=2)  # Limit to 2 calls per second
    def rate_limited_function():
        nonlocal call_count
        call_count += 1
        return f"Call {call_count}"
    
    print("   Making 5 rate-limited calls (should take ~2 seconds):")
    start_time = time.time()
    
    for _ in range(5):
        result = rate_limited_function()
        print(f"   - {result}")
    
    duration = time.time() - start_time
    print(f"   Completed in {duration:.2f} seconds")
    
    # 4. Build a transaction (without sending)
    print("\n4. Building a transaction...")
    to_address = "0x" + "f" * 40  # A dummy address
    tx_params = wallet.build_transaction(
        to=to_address,
        value=1000000000000000,  # 0.001 ETH in wei
        gas=21000,
        max_fee_per_gas=2000000000,  # 2 Gwei
        max_priority_fee_per_gas=1000000000  # 1 Gwei
    )
    
    print("   Transaction parameters:")
    for key, value in tx_params.items():
        print(f"   - {key}: {value}")
    
    print("\nDemo complete!")

if __name__ == "__main__":
    main() 