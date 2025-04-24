#!/usr/bin/env python3

"""
Simplified test script to verify basic connectivity with Ethereum RPC endpoints.
This script focuses on essential functionality and is suitable for testing local nodes.
"""

import sys
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware

def test_rpc_endpoint(url):
    """
    Test if an RPC endpoint is accessible and functioning correctly.
    
    Args:
        url: RPC endpoint URL
        
    Returns:
        bool: True if the basic tests pass, False otherwise
    """
    print(f"\n===== Testing RPC endpoint: {url} =====")
    
    # Connect to the RPC endpoint
    if url.startswith('http'):
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))
    elif url.startswith('ws'):
        w3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=10))
    else:
        print(f"ERROR: Unsupported URL scheme: {url}")
        return False
    
    # Add POA middleware for compatibility with various networks
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    try:
        is_connected = w3.is_connected()
        if is_connected:
            print(f"SUCCESS: Connection established")
        else:
            print(f"ERROR: Connection failed")
            return False
    except Exception as e:
        print(f"ERROR: Connection error: {str(e)}")
        return False
    
    # Test 2: Get network version/chain ID
    print("\n2. Testing chain ID retrieval...")
    try:
        chain_id = w3.eth.chain_id
        print(f"SUCCESS: Network chain ID: {chain_id}")
    except Exception as e:
        print(f"ERROR: Failed to get chain ID: {str(e)}")
        return False
    
    # Test 3: Get block number
    print("\n3. Testing block number retrieval...")
    try:
        block_number = w3.eth.block_number
        print(f"SUCCESS: Current block number: {block_number}")
    except Exception as e:
        print(f"ERROR: Failed to get block number: {str(e)}")
        return False
    
    print("\n===== Basic connectivity tests completed successfully =====")
    return True

def main():
    """Test RPC endpoints specified by command line arguments or default to localhost."""
    # Default to localhost if no arguments provided
    urls = sys.argv[1:] if len(sys.argv) > 1 else ["http://localhost:8545"]
    
    # Print usage information
    if urls == ["http://localhost:8545"]:
        print("No RPC URL provided. Testing local RPC endpoint (http://localhost:8545).")
        print("Usage: python test_local_rpc.py [rpc_url1] [rpc_url2] ...")
    
    # Test each endpoint
    results = {}
    for url in urls:
        results[url] = test_rpc_endpoint(url)
    
    # Print summary
    print("\n===== Summary =====")
    all_passed = True
    for url, result in results.items():
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{url}: {status}")
    
    # Exit with appropriate code
    if all_passed:
        print("\nAll RPC endpoints are working correctly.")
        sys.exit(0)
    else:
        print("\nSome RPC endpoints failed the tests.")
        sys.exit(1)

if __name__ == "__main__":
    main() 