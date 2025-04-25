"""Module for handling Ethereum smart contract interactions."""

import json
from typing import Any, Dict, List, Optional, Union

from web3 import Web3
from web3.contract import Contract
from web3.types import ABI, ABIFunction


def load_contract(web3: Web3, address: str, abi: Union[str, List, Dict]) -> Contract:
    """Load a contract from its address and ABI.
    
    Args:
        web3: Web3 instance
        address: Contract address
        abi: Contract ABI as JSON string, list or dict
        
    Returns:
        Contract instance
    """
    # Convert address to checksum
    address = Web3.to_checksum_address(address)
    
    # Parse ABI if it's a string
    if isinstance(abi, str):
        abi = json.loads(abi)
    
    # Create and return contract instance
    return web3.eth.contract(address=address, abi=abi)


def get_function_signature(function_name: str, abi: Union[str, List, Dict]) -> str:
    """Get the function signature from the ABI.
    
    Args:
        function_name: Name of the function
        abi: Contract ABI as JSON string, list or dict
        
    Returns:
        Function signature as a string
    """
    # Parse ABI if it's a string
    if isinstance(abi, str):
        abi = json.loads(abi)
    
    # Find the function in the ABI
    for item in abi:
        if item.get("type") == "function" and item.get("name") == function_name:
            # Build function signature
            inputs = item.get("inputs", [])
            param_types = [inp.get("type") for inp in inputs]
            return f"{function_name}({','.join(param_types)})"
    
    raise ValueError(f"Function {function_name} not found in ABI")


def encode_function_call(
    web3: Web3, 
    function_name: str, 
    abi: Union[str, List, Dict], 
    args: List[Any] = None
) -> str:
    """Encode a function call for contract interaction.
    
    Args:
        web3: Web3 instance
        function_name: Name of the function to call
        abi: Contract ABI as JSON string, list or dict
        args: Arguments to pass to the function
        
    Returns:
        Encoded function call in hex format
    """
    # Parse ABI if it's a string
    if isinstance(abi, str):
        abi = json.loads(abi)
    
    # Create a contract without an address
    contract = web3.eth.contract(abi=abi)
    
    # Get the function
    contract_function = getattr(contract.functions, function_name)
    
    # Build the function call with arguments
    if args is None:
        args = []
    
    function_call = contract_function(*args)
    
    # Encode the function call
    return function_call.build_transaction({'gas': 0})['data'] 