#!/usr/bin/env python3
"""
Wallet Pool Example

This example demonstrates how to use the wallet pool functionality to manage
multiple wallets with different selection strategies.
"""

from py_spamoor import Wallet, WalletPool, WalletSelectionMode, Client, ClientConfig


def main():
    # Create some test wallets
    wallets = [
        Wallet(),  # Random wallet 1
        Wallet(),  # Random wallet 2
        Wallet(),  # Random wallet 3
    ]
    
    # Print wallet addresses
    print("Created wallets:")
    for i, wallet in enumerate(wallets):
        print(f"Wallet {i+1}: {wallet.get_address()}")
    
    # Create client configs
    client_configs = [
        ClientConfig(url="http://localhost:8545", name="node1", group="dev"),
        ClientConfig(url="http://localhost:8546", name="node2", group="dev"),
    ]
    
    # Create a wallet pool with round-robin selection
    print("\nCreating wallet pool with ROUND_ROBIN selection...")
    rr_pool = WalletPool(
        wallets=wallets, 
        wallet_selection_mode=WalletSelectionMode.ROUND_ROBIN
    )
    
    # Get wallets from the pool
    print("Selecting wallets from round-robin pool:")
    for _ in range(5):
        selected_wallet = rr_pool.get_wallet()
        print(f"Selected wallet: {selected_wallet.get_address()}")
    
    # Create a wallet pool with random selection
    print("\nCreating wallet pool with RANDOM selection...")
    random_pool = WalletPool(
        wallets=wallets, 
        wallet_selection_mode=WalletSelectionMode.RANDOM
    )
    
    # Get wallets from the pool
    print("Selecting wallets from random pool:")
    for _ in range(5):
        selected_wallet = random_pool.get_wallet()
        print(f"Selected wallet: {selected_wallet.get_address()}")


if __name__ == "__main__":
    main() 