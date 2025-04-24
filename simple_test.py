#!/usr/bin/env python3

"""
Simple test script to verify that py_spamoor is correctly installed.
"""

from py_spamoor import Wallet, ClientConfig, Client, rate_limited

def main():
    # Test imports
    print("Successfully imported py_spamoor modules")
    
    # Test creating a wallet
    wallet = Wallet("0x0000000000000000000000000000000000000000000000000000000000000001")
    print(f"Created wallet with address: {wallet.get_address()}")
    
    # Test creating a client config
    config = ClientConfig(url="http://localhost:8545", name="test", group="default")
    print(f"Created client config with name: {config.name}")
    
    # Test rate limiter
    @rate_limited(calls_per_second=10)
    def test_function():
        return "Rate limiter works!"
    
    result = test_function()
    print(result)
    
    print("All basic functionality tests passed!")

if __name__ == "__main__":
    main() 