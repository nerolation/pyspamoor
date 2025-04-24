#!/usr/bin/env python3
"""
Basic Wallet Example

This example demonstrates how to create a wallet and perform basic operations.
"""

from py_spamoor import Wallet


def main():
    # Create a new random wallet
    print("Creating a new wallet...")
    new_wallet = Wallet()
    print(f"New wallet address: {new_wallet.get_address()}")
    
    # Load a wallet from private key
    # WARNING: Never hardcode private keys in production code
    test_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
    print("\nLoading wallet from private key...")
    wallet = Wallet(test_key)
    print(f"Wallet address: {wallet.get_address()}")
    
    # Build a transaction
    print("\nBuilding a transaction...")
    tx_params = wallet.build_transaction(
        to="0xffffffffffffffffffffffffffffffffffffffff",
        value=1000000000000000,  # 0.001 ETH in wei
        gas=21000,
        max_fee_per_gas=2000000000,  # 2 Gwei
        max_priority_fee_per_gas=1000000000  # 1 Gwei
    )
    print(f"Transaction parameters: {tx_params}")
    
    # Sign the transaction
    print("\nSigning the transaction...")
    signed_tx = wallet.sign_transaction(tx_params)
    print(f"Signed transaction: {signed_tx}")
    
    print("\nIn a real application, you would now send this transaction to the network.")


if __name__ == "__main__":
    main() 