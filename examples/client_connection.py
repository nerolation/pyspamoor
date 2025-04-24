#!/usr/bin/env python3
"""
Client Connection Example

This example demonstrates how to connect to an Ethereum node and interact with it.
"""

from py_spamoor import Client, ClientConfig


def main():
    # Create a client configuration
    print("Creating client configuration...")
    client_config = ClientConfig(
        url="http://localhost:8545",  # Your Ethereum node RPC URL
        name="local_node",
        group="development"
    )
    
    # Initialize client
    print("\nInitializing client...")
    client = Client(client_config)
    
    # Get the current block number
    print("\nQuerying the blockchain...")
    try:
        block_number = client.get_block_number()
        print(f"Current block number: {block_number}")
        
        # Get the gas price
        gas_price = client.get_gas_price()
        print(f"Current gas price: {gas_price} wei")
        
        # Get chain ID
        chain_id = client.get_chain_id()
        print(f"Chain ID: {chain_id}")
    except Exception as e:
        print(f"Error connecting to the node: {e}")
        print("Make sure your Ethereum node is running and accessible.")


if __name__ == "__main__":
    main() 