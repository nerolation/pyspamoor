"""Utility functions for py_spamoor."""

import json
import os
import random
import time
from typing import Any, Dict, List, Optional, Union

from web3 import Web3
from web3.middleware import geth_poa_middleware


def random_delay(min_delay: float = 0.5, max_delay: float = 3.0) -> None:
    """Sleep for a random duration between min_delay and max_delay.
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    if min_delay <= 0 or max_delay <= 0:
        return
    
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def load_json_file(file_path: str) -> Any:
    """Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return json.load(f)


def write_json_file(file_path: str, data: Any) -> None:
    """Write JSON data to a file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to write
        
    Raises:
        IOError: If the file can't be written
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def derive_address_from_private_key(private_key: str) -> str:
    """Derive Ethereum address from a private key.
    
    Args:
        private_key: Private key (with or without 0x prefix)
        
    Returns:
        Ethereum address
    """
    # Ensure the private key has the 0x prefix
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    # Create a temporary Web3 instance to derive the address
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    return account.address


def connect_web3(rpc_endpoint: str) -> Web3:
    """Connect to an Ethereum node via RPC.
    
    Args:
        rpc_endpoint: RPC endpoint URL
        
    Returns:
        Connected Web3 instance
        
    Raises:
        ValueError: If connection fails
    """
    provider = Web3.HTTPProvider(rpc_endpoint)
    w3 = Web3(provider)
    
    # Add middleware for PoA chains (like Binance Smart Chain, Polygon, etc.)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Check connection
    if not w3.is_connected():
        raise ValueError(f"Failed to connect to RPC endpoint: {rpc_endpoint}")
    
    return w3


def load_private_keys(key_input: str) -> List[str]:
    """Load private keys from a file or a direct input.
    
    Args:
        key_input: Path to a file containing private keys (one per line) or a direct private key
        
    Returns:
        List of private keys
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If no valid keys are found
    """
    keys = []
    
    # Check if the input is a path to a file
    if os.path.exists(key_input) and os.path.isfile(key_input):
        with open(key_input, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove 0x prefix if present
                    if line.startswith('0x'):
                        line = line[2:]
                    keys.append(line)
    else:
        # Treat as direct key input
        key = key_input.strip()
        if key.startswith('0x'):
            key = key[2:]
        keys.append(key)
    
    if not keys:
        raise ValueError("No valid private keys found")
    
    return keys


def load_rpc_endpoints(rpc_input: str) -> List[str]:
    """Load RPC endpoints from a file or a direct input.
    
    Args:
        rpc_input: Path to a file containing RPC endpoints (one per line) or a direct RPC endpoint
        
    Returns:
        List of RPC endpoints
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If no valid endpoints are found
    """
    endpoints = []
    
    # Check if the input is a path to a file
    if os.path.exists(rpc_input) and os.path.isfile(rpc_input):
        with open(rpc_input, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    endpoints.append(line)
    else:
        # Treat as direct endpoint input
        endpoints.append(rpc_input.strip())
    
    if not endpoints:
        raise ValueError("No valid RPC endpoints found")
    
    return endpoints 