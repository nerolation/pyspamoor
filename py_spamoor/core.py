"""Core implementation of the py_spamoor client."""

import json
import os
import random
import time
from typing import Any, Dict, List, Optional, Union, Tuple

from web3 import Web3
from web3.exceptions import TransactionNotFound
from web3.types import TxParams, Wei

from py_spamoor.utils import (
    load_private_keys,
    load_rpc_endpoints,
    connect_web3,
    random_delay,
    derive_address_from_private_key,
    load_json_file,
    write_json_file,
)


class SpamoorClient:
    """Main client for py_spamoor operations."""
    
    def __init__(
        self,
        private_keys: List[str],
        rpc_endpoints: List[str],
        chain_id: Optional[int] = None,
        gas_price: Optional[int] = None,
        gas_limit: int = 300000,
        dry_run: bool = False,
        verbose: bool = False,
        delay_min: float = 0.5,
        delay_max: float = 3.0,
        max_retries: int = 3,
    ):
        """Initialize the SpamoorClient.
        
        Args:
            private_keys: List of private keys
            rpc_endpoints: List of RPC endpoint URLs
            chain_id: Chain ID (if None, will be auto-detected)
            gas_price: Gas price in Gwei (if None, will be auto-detected)
            gas_limit: Gas limit for transactions
            dry_run: If True, don't send transactions
            verbose: If True, print verbose output
            delay_min: Minimum delay between transactions in seconds
            delay_max: Maximum delay between transactions in seconds
            max_retries: Maximum number of retries for failed transactions
        """
        self.private_keys = private_keys
        self.rpc_endpoints = rpc_endpoints
        self.manual_chain_id = chain_id
        self.manual_gas_price = gas_price
        self.gas_limit = gas_limit
        self.dry_run = dry_run
        self.verbose = verbose
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        
        # Initialize web3 connections
        self.web3_instances = []
        for endpoint in self.rpc_endpoints:
            self.web3_instances.append(connect_web3(endpoint))
        
        # Generate wallet addresses
        self.addresses = [derive_address_from_private_key(pk) for pk in self.private_keys]
        
        if self.verbose:
            print(f"Initialized with {len(self.private_keys)} accounts and {len(self.rpc_endpoints)} RPC endpoints")
            for i, addr in enumerate(self.addresses):
                print(f"Account {i+1}: {addr}")
    
    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> "SpamoorClient":
        """Create a SpamoorClient from parsed command-line arguments.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            An initialized SpamoorClient
        """
        # Load private keys
        if "private_key" in args and args["private_key"]:
            private_keys = load_private_keys(args["private_key"])
        elif "key_file" in args and args["key_file"]:
            private_keys = load_private_keys(args["key_file"])
        else:
            raise ValueError("No private keys provided")
        
        # Load RPC endpoints
        if "rpc_endpoint" in args and args["rpc_endpoint"]:
            rpc_endpoints = load_rpc_endpoints(args["rpc_endpoint"])
        elif "rpc_file" in args and args["rpc_file"]:
            rpc_endpoints = load_rpc_endpoints(args["rpc_file"])
        else:
            raise ValueError("No RPC endpoints provided")
        
        # Create client
        return cls(
            private_keys=private_keys,
            rpc_endpoints=rpc_endpoints,
            chain_id=args.get("chain_id"),
            gas_price=args.get("gas_price"),
            gas_limit=args.get("gas_limit", 300000),
            dry_run=args.get("dry_run", False),
            verbose=args.get("verbose", False),
            delay_min=args.get("delay_min", 0.5),
            delay_max=args.get("delay_max", 3.0),
            max_retries=args.get("max_retries", 3),
        )
    
    def get_random_web3(self) -> Web3:
        """Get a random Web3 instance.
        
        Returns:
            A randomly selected Web3 instance
        """
        return random.choice(self.web3_instances)
    
    def get_chain_id(self, web3: Web3) -> int:
        """Get the chain ID for a Web3 connection.
        
        Args:
            web3: Web3 instance
            
        Returns:
            Chain ID
        """
        if self.manual_chain_id is not None:
            return self.manual_chain_id
        return web3.eth.chain_id
    
    def get_gas_price(self, web3: Web3) -> int:
        """Get the gas price for a Web3 connection.
        
        Args:
            web3: Web3 instance
            
        Returns:
            Gas price in Wei
        """
        if self.manual_gas_price is not None:
            return Web3.to_wei(self.manual_gas_price, 'gwei')
        return web3.eth.gas_price
    
    def build_transaction(
        self, 
        web3: Web3, 
        from_address: str, 
        to_address: str, 
        value: Wei = 0, 
        data: str = "",
        nonce: Optional[int] = None,
    ) -> TxParams:
        """Build a transaction object.
        
        Args:
            web3: Web3 instance
            from_address: Sender address
            to_address: Recipient address
            value: Value in Wei
            data: Transaction data
            nonce: Transaction nonce (if None, will be auto-detected)
            
        Returns:
            Transaction parameters
        """
        if nonce is None:
            nonce = web3.eth.get_transaction_count(from_address)
        
        chain_id = self.get_chain_id(web3)
        gas_price = self.get_gas_price(web3)
        
        tx_params = {
            'from': from_address,
            'to': to_address,
            'value': value,
            'gas': self.gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': chain_id,
        }
        
        if data:
            tx_params['data'] = data
        
        return tx_params
    
    def sign_transaction(self, web3: Web3, tx_params: TxParams, private_key: str) -> str:
        """Sign a transaction.
        
        Args:
            web3: Web3 instance
            tx_params: Transaction parameters
            private_key: Private key to sign with
            
        Returns:
            Signed transaction
        """
        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        return signed_tx.rawTransaction.hex()
    
    def send_transaction(self, web3: Web3, signed_tx: str, retry_count: int = 0) -> str:
        """Send a signed transaction.
        
        Args:
            web3: Web3 instance
            signed_tx: Signed transaction
            retry_count: Current retry count
            
        Returns:
            Transaction hash
            
        Raises:
            Exception: If transaction fails after max retries
        """
        if self.dry_run:
            if self.verbose:
                print(f"[DRY RUN] Would send transaction: {signed_tx[:10]}...")
            return "0x" + "0" * 64  # Dummy hash for dry run
        
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx)
            tx_hash_hex = tx_hash.hex()
            if self.verbose:
                print(f"Transaction sent: {tx_hash_hex}")
            return tx_hash_hex
        except Exception as e:
            if retry_count >= self.max_retries:
                raise Exception(f"Failed to send transaction after {self.max_retries} retries: {e}")
            
            if self.verbose:
                print(f"Transaction failed, retrying ({retry_count + 1}/{self.max_retries}): {e}")
            
            random_delay(self.delay_min, self.delay_max)
            return self.send_transaction(web3, signed_tx, retry_count + 1)
    
    def wait_for_receipt(self, web3: Web3, tx_hash: str, timeout: int = 120) -> Dict[str, Any]:
        """Wait for a transaction receipt.
        
        Args:
            web3: Web3 instance
            tx_hash: Transaction hash
            timeout: Timeout in seconds
            
        Returns:
            Transaction receipt
            
        Raises:
            TransactionNotFound: If transaction is not found
            TimeoutError: If timeout is reached
        """
        if self.dry_run:
            return {"status": 1, "transactionHash": tx_hash}
        
        start_time = time.time()
        while True:
            try:
                receipt = web3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    if self.verbose:
                        status = "Success" if receipt.status == 1 else "Failed"
                        print(f"Transaction {tx_hash} {status}. Block: {receipt.blockNumber}")
                    return dict(receipt)
            except TransactionNotFound:
                pass
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for receipt of {tx_hash}")
            
            time.sleep(2)
    
    def execute_read_operations(self) -> List[Dict[str, Any]]:
        """Execute read-only operations.
        
        Returns:
            List of operation results
        """
        results = []
        
        for address in self.addresses:
            web3 = self.get_random_web3()
            
            # Get account balance
            balance = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance, "ether")
            
            result = {
                "address": address,
                "balance_wei": balance,
                "balance_eth": balance_eth,
                "chain_id": self.get_chain_id(web3),
            }
            
            if self.verbose:
                print(f"Address: {address}")
                print(f"Balance: {balance_eth} ETH")
            
            results.append(result)
            random_delay(self.delay_min, self.delay_max)
        
        return results
    
    def execute_write_operations(self) -> List[Dict[str, Any]]:
        """Execute write operations (send ETH transactions).
        
        Returns:
            List of transaction receipts
        """
        results = []
        
        # Pair senders and receivers (circular)
        pairs = []
        for i in range(len(self.addresses)):
            sender = self.addresses[i]
            receiver = self.addresses[(i + 1) % len(self.addresses)]
            sender_key = self.private_keys[i]
            pairs.append((sender, sender_key, receiver))
        
        for sender, key, receiver in pairs:
            web3 = self.get_random_web3()
            
            # Send a minimal amount of ETH
            value = Web3.to_wei(0.0001, "ether")
            
            # Build and send transaction
            tx_params = self.build_transaction(
                web3=web3,
                from_address=sender,
                to_address=receiver,
                value=value,
            )
            
            signed_tx = self.sign_transaction(web3, tx_params, key)
            tx_hash = self.send_transaction(web3, signed_tx)
            
            receipt = self.wait_for_receipt(web3, tx_hash)
            results.append(receipt)
            
            random_delay(self.delay_min, self.delay_max)
        
        return results
    
    def execute_token_approvals(self) -> List[Dict[str, Any]]:
        """Execute token approvals.
        
        Returns:
            List of transaction receipts
        """
        # Standard ERC20 approve function signature
        approve_signature = "0x095ea7b3"
        
        # Common tokens to approve (example addresses - should be configured based on chain)
        token_addresses = {
            # Mainnet tokens
            1: [
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
                "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            ],
            # Test networks don't have standard tokens
        }
        
        results = []
        
        for i, address in enumerate(self.addresses):
            web3 = self.get_random_web3()
            chain_id = self.get_chain_id(web3)
            
            # Get tokens for this chain
            chain_tokens = token_addresses.get(chain_id, [])
            if not chain_tokens:
                if self.verbose:
                    print(f"No token addresses configured for chain ID {chain_id}")
                continue
            
            for token in chain_tokens:
                # Build approve call with max uint256 amount
                spender = "0x0000000000000000000000000000000000000000"  # Replace with actual spender
                max_approval = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
                
                # ERC20 approve(address,uint256)
                data = (
                    approve_signature +  
                    "000000000000000000000000" + spender[2:].lower() +
                    max_approval
                )
                
                tx_params = self.build_transaction(
                    web3=web3,
                    from_address=address,
                    to_address=token,
                    data=data,
                )
                
                signed_tx = self.sign_transaction(web3, tx_params, self.private_keys[i])
                tx_hash = self.send_transaction(web3, signed_tx)
                
                receipt = self.wait_for_receipt(web3, tx_hash)
                results.append(receipt)
                
                random_delay(self.delay_min, self.delay_max)
        
        return results
    
    def execute_custom_function(self, abi_file: str = None, contract_address: str = None, 
                               function_name: str = None, function_args: str = None) -> Dict[str, Any]:
        """Execute a custom contract function.
        
        Args:
            abi_file: Path to ABI file
            contract_address: Contract address
            function_name: Function name
            function_args: Comma-separated function arguments
            
        Returns:
            Function execution result
        """
        # Parse from instance variables if not provided
        if abi_file is None:
            abi_file = getattr(self, 'abi_file', None)
        if contract_address is None:
            contract_address = getattr(self, 'contract_address', None)
        if function_name is None:
            function_name = getattr(self, 'function_name', None)
        if function_args is None:
            function_args = getattr(self, 'function_args', None)
        
        # Validate required parameters
        if not abi_file or not contract_address or not function_name:
            raise ValueError("Missing required parameters: abi_file, contract_address, function_name")
        
        # Load ABI
        abi = load_json_file(abi_file)
        
        # Parse function arguments
        args = []
        if function_args:
            if isinstance(function_args, str):
                args = [arg.strip() for arg in function_args.split(',')]
            elif isinstance(function_args, list):
                args = function_args
        
        results = []
        
        for i, address in enumerate(self.addresses):
            web3 = self.get_random_web3()
            
            # Create contract instance
            contract = web3.eth.contract(address=contract_address, abi=abi)
            
            # Get function object
            contract_func = getattr(contract.functions, function_name)
            
            # Call the function
            try:
                if self.verbose:
                    print(f"Calling {function_name} with args: {args}")
                
                # Check if function is view/pure (read-only)
                func_abi = next((item for item in abi if item.get('name') == function_name), None)
                is_read_only = False
                
                if func_abi:
                    state_mutability = func_abi.get('stateMutability', '')
                    is_read_only = state_mutability in ('view', 'pure')
                
                if is_read_only:
                    # For read-only functions, just call them
                    result = contract_func(*args).call({'from': address})
                    results.append({
                        'address': address,
                        'result': result,
                        'success': True
                    })
                else:
                    # For state-changing functions, build and send a transaction
                    tx = contract_func(*args).build_transaction({
                        'from': address,
                        'gas': self.gas_limit,
                        'gasPrice': self.get_gas_price(web3),
                        'nonce': web3.eth.get_transaction_count(address),
                        'chainId': self.get_chain_id(web3),
                    })
                    
                    signed_tx = self.sign_transaction(web3, tx, self.private_keys[i])
                    tx_hash = self.send_transaction(web3, signed_tx)
                    
                    receipt = self.wait_for_receipt(web3, tx_hash)
                    results.append({
                        'address': address,
                        'tx_hash': tx_hash,
                        'receipt': receipt,
                        'success': receipt.get('status') == 1
                    })
                
                random_delay(self.delay_min, self.delay_max)
                
            except Exception as e:
                if self.verbose:
                    print(f"Error calling {function_name}: {e}")
                results.append({
                    'address': address,
                    'error': str(e),
                    'success': False
                })
        
        return results 