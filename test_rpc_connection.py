#!/usr/bin/env python3

"""
Test script to verify connectivity and basic functionality with Ethereum RPC endpoints.
"""

import sys
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware

def test_rpc_endpoint(url, description="RPC Endpoint"):
    """
    Test if an RPC endpoint is accessible and functioning correctly.
    
    Args:
        url: RPC endpoint URL
        description: Human-readable description of the endpoint
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print(f"\n===== Testing {description} ({url}) =====")
    
    # Connect to the RPC endpoint
    if url.startswith('http'):
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10}))
    elif url.startswith('ws'):
        w3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=10))
    else:
        print(f"❌ Unsupported URL scheme: {url}")
        return False
    
    # Add POA middleware for compatibility with networks like Goerli
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    try:
        is_connected = w3.is_connected()
        if is_connected:
            print(f"✅ Connection successful")
        else:
            print(f"❌ Connection failed")
            return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False
    
    # Test 2: Get network version/chain ID
    print("\n2. Testing network version...")
    try:
        chain_id = w3.eth.chain_id
        print(f"✅ Network chain ID: {chain_id}")
    except Exception as e:
        print(f"❌ Failed to get chain ID: {str(e)}")
        return False
    
    # Test 3: Get latest block
    print("\n3. Testing block retrieval...")
    try:
        start_time = time.time()
        latest_block = w3.eth.get_block('latest')
        elapsed = time.time() - start_time
        
        print(f"✅ Latest block: {latest_block.number}")
        print(f"   Block timestamp: {latest_block.timestamp}")
        print(f"   Block retrieval time: {elapsed:.2f} seconds")
    except Exception as e:
        print(f"❌ Failed to get latest block: {str(e)}")
        return False
    
    # Test 4: Get account balance (using a known address like Vitalik's)
    print("\n4. Testing balance retrieval...")
    try:
        # Vitalik's address as an example
        vitalik_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        start_time = time.time()
        balance = w3.eth.get_balance(vitalik_address)
        elapsed = time.time() - start_time
        
        print(f"✅ Balance of {vitalik_address}: {w3.from_wei(balance, 'ether')} ETH")
        print(f"   Balance retrieval time: {elapsed:.2f} seconds")
    except Exception as e:
        print(f"❌ Failed to get balance: {str(e)}")
        return False
    
    # Test 5: Get gas price / fee estimates
    print("\n5. Testing fee estimation...")
    try:
        start_time = time.time()
        
        if hasattr(w3.eth, 'gas_price'):
            gas_price = w3.eth.gas_price
            print(f"✅ Gas price: {w3.from_wei(gas_price, 'gwei')} Gwei")
        
        # For EIP-1559 networks
        if 'baseFeePerGas' in w3.eth.get_block('latest'):
            base_fee = w3.eth.get_block('latest')['baseFeePerGas']
            print(f"✅ Base fee: {w3.from_wei(base_fee, 'gwei')} Gwei")
            
            if hasattr(w3.eth, 'max_priority_fee'):
                priority_fee = w3.eth.max_priority_fee
                print(f"✅ Priority fee: {w3.from_wei(priority_fee, 'gwei')} Gwei")
        
        elapsed = time.time() - start_time
        print(f"   Fee estimation time: {elapsed:.2f} seconds")
    except Exception as e:
        print(f"⚠️ Fee estimation had issues: {str(e)}")
        # Don't fail the test for this, as some networks might have different fee models
    
    print("\n===== All tests completed successfully =====")
    return True

def main():
    """Test RPC endpoints specified by command line arguments or defaults."""
    # Default RPC endpoints to test
    default_endpoints = [
        {
            "url": "https://eth.llamarpc.com",
            "description": "LlamaRPC Mainnet"
        },
        {
            "url": "https://rpc.ankr.com/eth_sepolia",
            "description": "Ankr Sepolia Testnet"
        }
    ]
    
    # Use command-line arguments if provided
    endpoints = []
    if len(sys.argv) > 1:
        for url in sys.argv[1:]:
            endpoints.append({"url": url, "description": f"Custom Endpoint ({url})"})
    else:
        endpoints = default_endpoints
        print("No RPC URLs provided. Testing default endpoints.")
        print("Usage: python test_rpc_connection.py [rpc_url1] [rpc_url2] ...")
    
    # Test each endpoint
    results = []
    for endpoint in endpoints:
        result = test_rpc_endpoint(endpoint["url"], endpoint["description"])
        results.append((endpoint["description"], result))
    
    # Print summary
    print("\n===== Summary =====")
    all_passed = True
    for description, result in results:
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{description}: {status}")
    
    # Exit with appropriate code
    if all_passed:
        print("\nAll endpoints passed the tests.")
        sys.exit(0)
    else:
        print("\nSome endpoints failed the tests.")
        sys.exit(1)

if __name__ == "__main__":
    main() 