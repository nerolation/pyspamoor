"""
Ethereum wallet management for py_spamoor.
"""
from typing import Dict, Any, Union

from web3 import Web3
from eth_account import Account
from web3.types import TxParams, HexBytes
from py_spamoor.client import Client

class Wallet:
    """Wrapper for an Ethereum wallet with operations needed for transactions."""

    def __init__(self, private_key: str):
        """
        Initialize a wallet with a private key.
        
        Args:
            private_key: Private key (with or without 0x prefix)
        """
        # Ensure private key has 0x prefix
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
            
        self.account = Account.from_key(private_key)
        self.address = self.account.address
    
    def get_address(self) -> str:
        """Get wallet address."""
        return self.address
        
    def build_transaction(self, to: str, **kwargs) -> TxParams:
        """
        Build an EIP-1559 transaction.
        
        Args:
            to: Recipient address
            value: Amount to send in wei (default: 0)
            gas: Gas limit (default: 21000)
            max_fee_per_gas: Maximum fee per gas in wei
            max_priority_fee_per_gas: Maximum priority fee per gas in wei
            data: Transaction data hexstring
            nonce: Transaction nonce (optional)
            
        Returns:
            Transaction parameters dictionary ready for signing
        """
        tx_params = {
            "to": to,
            "value": kwargs.get("value", 0),
            "gas": kwargs.get("gas", 21000),
            "maxFeePerGas": kwargs.get("max_fee_per_gas", 1000000000),
            "maxPriorityFeePerGas": kwargs.get("max_priority_fee_per_gas", 1000000000),
            "chainId": kwargs.get("chain_id", 3151908),  # Default to mainnet
            "type": 2,  # EIP-1559 transaction,
        }
        
        # Add data field if provided
        if kwargs.get("data") is not None:
            tx_params["data"] = kwargs["data"]
        
        # Add nonce if provided
        if kwargs.get("nonce") is not None:
            tx_params["nonce"] = kwargs["nonce"]
            
        # Add nonce if provided
        if kwargs.get("accessList") is not None:
            tx_params["accessList"] = kwargs["accessList"]
            
        if kwargs.get("blob_data"):
            if max_fee_per_blob_gas is None:
                raise ValueError("max_fee_per_blob_gas is required when using blob_data_list")
            tx.update({
                "type": 3,
                "maxFeePerBlobGas": kwargs.get("max_fee_per_blob_gas", 1000000000),
            })
            tx_params["_blobs"] = kwargs.get("blob_data")
            
        return tx_params
    
    def sign_transaction(self, tx_params: TxParams, client: Client) -> HexBytes:
        """
        Sign a transaction.
        
        Args:
            tx_params: Transaction parameters
            
        Returns:
            Signed transaction
        """
        if not "nonce" in tx_params.keys():
            tx_params["nonce"] = client.w3.eth.get_transaction_count(self.account.address)
        if "maxFeePerBlobGas" in tx_params.keys():
            blob_data = tx_params["_blobs"]
            del tx_params["_blobs"]
            signed_tx = self.account.sign_transaction(tx_params, blobs=blob_data)
        else:
            signed_tx = self.account.sign_transaction(tx_params)
        return signed_tx.rawTransaction
    