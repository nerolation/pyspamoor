"""Module for handling Ethereum transactions."""

from typing import Dict, Any, Optional, Union

from web3 import Web3
from web3.types import TxParams, Wei


def build_transaction(
    web3: Web3,
    from_address: str,
    to_address: Optional[str],
    value: Wei = 0,
    gas_limit: int = 21000,
    gas_price: Optional[Wei] = None,
    max_fee_per_gas: Optional[Wei] = None,
    max_priority_fee_per_gas: Optional[Wei] = None,
    nonce: Optional[int] = None,
    data: str = "0x",
    chain_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Build an Ethereum transaction.
    
    Args:
        web3: Web3 instance
        from_address: Sender address
        to_address: Recipient address, None for contract creation
        value: Amount of ETH to send in Wei
        gas_limit: Gas limit for the transaction
        gas_price: Gas price in Wei for legacy transactions
        max_fee_per_gas: Max fee per gas in Wei for EIP-1559 transactions
        max_priority_fee_per_gas: Max priority fee per gas in Wei for EIP-1559 transactions
        nonce: Transaction nonce, if None will be fetched from the blockchain
        data: Transaction data in hex format
        chain_id: Chain ID, if None will be fetched from the blockchain
        
    Returns:
        Transaction dictionary
    """
    # Ensure from_address is checksum address
    from_address = Web3.to_checksum_address(from_address)
    
    # Ensure to_address is checksum address if not None (contract creation)
    if to_address is not None:
        to_address = Web3.to_checksum_address(to_address)
    
    # Get nonce if not provided
    if nonce is None:
        nonce = web3.eth.get_transaction_count(from_address)
    
    # Get chain_id if not provided
    if chain_id is None:
        chain_id = web3.eth.chain_id
    
    # Build transaction based on fee model
    if max_fee_per_gas is not None and max_priority_fee_per_gas is not None:
        # EIP-1559 transaction
        transaction = {
            "from": from_address,
            "nonce": nonce,
            "gas": gas_limit,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "chainId": chain_id,
            "value": value,
            "data": data,
        }
        
        # Only add 'to' for non-contract-creation transactions
        if to_address is not None:
            transaction["to"] = to_address
    else:
        # Legacy transaction
        transaction = {
            "from": from_address,
            "nonce": nonce,
            "gas": gas_limit,
            "chainId": chain_id,
            "value": value,
            "data": data,
        }
        
        # Only add 'to' for non-contract-creation transactions
        if to_address is not None:
            transaction["to"] = to_address
        
        # Use provided gas price or get from the network
        if gas_price is not None:
            transaction["gasPrice"] = gas_price
        else:
            transaction["gasPrice"] = web3.eth.gas_price
    
    return transaction


def sign_transaction(web3: Web3, transaction: Dict[str, Any], private_key: str) -> bytes:
    """Sign a transaction with a private key.
    
    Args:
        web3: Web3 instance
        transaction: Transaction dictionary
        private_key: Private key to sign with
        
    Returns:
        Signed transaction in bytes
    """
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    return signed_txn.rawTransaction


def send_transaction(web3: Web3, signed_transaction: bytes) -> bytes:
    """Send a signed transaction to the network.
    
    Args:
        web3: Web3 instance
        signed_transaction: Signed transaction in bytes
        
    Returns:
        Transaction hash
    """
    return web3.eth.send_raw_transaction(signed_transaction) 