#!/usr/bin/env python3

"""
Example script demonstrating how to send transactions to different networks
and RPC endpoints using py_spamoor.
"""

import time
from py_spamoor import Wallet, ClientConfig, Client, rate_limited

def main():
    print("=== py_spamoor Multi-Network Example ===")
    
    # Create a wallet (for testing only, never use this key in production)
    wallet = Wallet("0x0000000000000000000000000000000000000000000000000000000000000001")
    print(f"Wallet address: {wallet.get_address()}")
    
    # Create configurations for different networks
    networks = {
        "mainnet": {
            "url": "https://mainnet.infura.io/v3/YOUR_API_KEY",
            "chain_id": 1,
            "name": "Ethereum Mainnet"
        },
        "sepolia": {
            "url": "https://sepolia.infura.io/v3/YOUR_API_KEY",
            "chain_id": 11155111,
            "name": "Sepolia Testnet"
        },
        "arbitrum": {
            "url": "https://arb1.arbitrum.io/rpc",
            "chain_id": 42161,
            "name": "Arbitrum One"
        },
        "local": {
            "url": "http://localhost:8545",
            "chain_id": 1337,
            "name": "Local Development"
        }
    }
    
    # Create client instances
    clients = {}
    for network_id, network in networks.items():
        config = ClientConfig(
            url=network["url"],
            name=network_id,
            group="example"
        )
        clients[network_id] = Client(config)
        print(f"Created client for {network['name']}")
    
    # Function to prepare and sign a transaction for a specific network
    def prepare_transaction(network_id, to_address, value):
        network = networks[network_id]
        
        print(f"\nPreparing transaction for {network['name']}:")
        print(f"  Chain ID: {network['chain_id']}")
        print(f"  RPC URL: {network['url']}")
        
        try:
            # Use a fake nonce for demo purposes (in real usage, get this from the network)
            nonce = 0  # In production: clients[network_id].get_nonce(wallet.get_address())
            
            # Build transaction
            tx_params = wallet.build_transaction(
                to=to_address,
                value=value,
                gas=21000,
                max_fee_per_gas=2000000000,  # 2 Gwei
                max_priority_fee_per_gas=1000000000,  # 1 Gwei
                chain_id=network['chain_id'],
                nonce=nonce
            )
            
            # Sign transaction
            signed_tx = wallet.sign_transaction(tx_params)
            
            print("  Transaction signed successfully")
            
            return signed_tx
        except Exception as e:
            print(f"  Error: {str(e)}")
            return None
    
    # Example: Prepare transaction for each network
    # (Not actually sending to avoid spending real funds)
    # Use a valid Ethereum address format (20 bytes / 40 hex chars)
    to_address = "0x0000000000000000000000000000000000000000"
    value = 1000000000000000  # 0.001 ETH in wei
    
    for network_id in networks.keys():
        signed_tx = prepare_transaction(network_id, to_address, value)
        
        if signed_tx:
            print(f"  Transaction payload size: {len(signed_tx)} bytes")
            # To actually send the transaction, uncomment the following line:
            # tx_hash = clients[network_id].send_transaction(signed_tx)
            # print(f"  Transaction sent! Hash: {tx_hash.hex()}")
    
    print("\nExample completed!")
    print("To actually send transactions, uncomment the send_transaction lines")
    print("and update the RPC URLs with valid API keys.")

if __name__ == "__main__":
    main() 