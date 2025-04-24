"""
Ethereum client interface for py_spamoor.
"""
from typing import Optional, Union
from urllib.parse import urlparse

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import HexBytes

from py_spamoor.wallet import Wallet


class ClientConfig:
    """Configuration for an Ethereum client."""
    
    def __init__(self, url: str, name: str = None, group: str = "default", timeout: int = 30):
        """
        Initialize client configuration.
        
        Args:
            url: RPC URL
            name: Client name (defaults to hostname from URL)
            group: Client group for categorization
            timeout: Request timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.group = group
        
        if name:
            self.name = name
        else:
            # Parse URL to get a readable name
            parsed_url = urlparse(url)
            self.name = parsed_url.netloc.split('.')[0]


class Client:
    def __init__(self, config: ClientConfig):
        """
        Initialize a client with the given configuration.
        
        Args:
            config: Client configuration
        """
        self.config = config
        self.rpc_url = config.url
        self.timeout = config.timeout
        self.client_group = config.group
        self.name = config.name
        
        # Initialize Web3 provider
        if self.rpc_url.startswith('http'):
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={'timeout': self.timeout}))
        elif self.rpc_url.startswith('ws'):
            self.w3 = Web3(Web3.WebsocketProvider(self.rpc_url, websocket_timeout=self.timeout))
        else:
            raise ValueError(f"Unsupported RPC URL scheme: {self.rpc_url}")
            
        # Add POA middleware for compatibility with networks like Goerli
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Verify connection (commented out to avoid requiring a working RPC)
        # if not self.w3.is_connected():
        #     raise ConnectionError(f"Failed to connect to Ethereum node at {self.rpc_url}")
    
    def get_name(self) -> str:
        """Get the client name derived from the RPC URL."""
        return self.name
    
    def get_client_group(self) -> str:
        """Get the client group."""
        return self.client_group
    
    def get_web3(self) -> Web3:
        """Get the Web3 instance."""
        return self.w3
    
    def update_wallet(self, wallet: Wallet) -> None:
        """
        Update a wallet's information using this client.
        
        Args:
            wallet: Wallet to update
        """
        wallet.update_from_web3(self.w3)
    
    def get_nonce(self, address: str) -> int:
        """
        Get the confirmed nonce for an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            Current nonce
        """
        return self.w3.eth.get_transaction_count(address)
    
    def get_transaction_receipt(self, tx_hash) -> Optional[dict]:
        """
        Get a transaction receipt.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction receipt or None if not found
        """
        try:
            return self.w3.eth.get_transaction_receipt(tx_hash)
        except Exception:
            return None
            
    def send_transaction(self, signed_tx: Union[str, bytes, HexBytes]) -> HexBytes:
        """
        Send a signed transaction to the network.
        
        Args:
            signed_tx: Signed transaction data (hex string or bytes)
            
        Returns:
            Transaction hash
        """
        # Convert to bytes if it's a hex string
        if isinstance(signed_tx, str) and signed_tx.startswith('0x'):
            signed_tx = HexBytes(signed_tx)
            
        # Send the transaction
        return self.w3.eth.send_raw_transaction(signed_tx)
        
    def get_chain_id(self) -> int:
        """
        Get the chain ID of the connected network.
        
        Returns:
            Chain ID as an integer
        """
        return self.w3.eth.chain_id 