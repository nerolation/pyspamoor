"""
Wallet pool management for py_spamoor.
"""
import os
import random
import enum
import threading
from typing import List, Dict, Optional

from py_spamoor.wallet import Wallet
from py_spamoor.client import Client, ClientConfig
from py_spamoor.helper import load_private_keys, parse_el_rpc_endpoints


class WalletSelectionMode(enum.Enum):
    """Mode for selecting wallets."""
    BY_INDEX = 1
    RANDOM = 2
    ROUND_ROBIN = 3


class ClientSelectionMode(enum.Enum):
    """Mode for selecting clients."""
    BY_INDEX = 1
    RANDOM = 2
    ROUND_ROBIN = 3
    
    
class StrategySelectionMode(enum.Enum):
    """Mode for selecting strategies."""
    BY_INDEX = 1
    RANDOM = 2
    ROUND_ROBIN = 3
    
class Strategy(enum.Enum):
    STANDARD_TX = 0
    CALLDATA_ZEROS = 1
    CALLDATA_NON_ZEROS = 2
    CALLDATA_MIX = 3
    ACCESS_LIST = 4
    BLOBS = 5


class WalletPool:
    """Pool of wallets with various selection methods."""
    
    def __init__(self):
        """
        Initialize wallet pool.
        
        Args:
            clients: List of available clients
        """
        self.clients: List[Client] = []
        self.wallets: List[Wallet] = []
        self.strategies: List[Strategy] = []
        self.wallet_names: Dict[str, str] = {}  # address -> name mapping
        
        # State for selection modes
        self.max_wallets = 0
        self.rr_wallet_idx = 0
        self.rr_client_idx = 0
        self.rr_strategy_idx = 0
        self.selection_lock = threading.Lock()
    
    def load_private_key_from_file(self, file_path: str) -> None:
        """
        Load private keys from a file.
        
        Args:
            file_path: Path to file containing private keys (one per line)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Private key file not found: {file_path}")

        # Filter out empty lines and comments
        accounts = load_private_keys(file_path)
        
        # Clear existing wallets
        self.wallets = []
        
        # Create wallets
        for i, acc in enumerate(accounts):
            wallet = Wallet(acc["private_key"])
            self.wallets.append(wallet)
            self.wallet_names[wallet.get_address()] = f"wallet_{i+1}"
        
        self.max_wallets = len(self.wallets)
        
    def load_clients_from_file(self, file_path: str) -> None:
        """
        Load clients from a file.
        
        Args:
            file_path: Path to file containing the rpcs endpoints outputed by kurtosis
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"RPC file not found: {file_path}")
        
        # Filter out empty lines and comments
        rpcs = parse_el_rpc_endpoints(file_path)
        
        # Clear existing wallets
        self.clients = [Client(j) for j in [ClientConfig(rpcs[i], i) for i in rpcs]]
        
    def add_strategy(self, strategies: List[Strategy]) -> None:
        for stategy in strategies:
            self.strategies.append(stategy)
       
    def get_wallet(self, mode: WalletSelectionMode, input_val: int = 0) -> Optional[Wallet]:
        """
        Get a wallet using the specified selection mode.
        
        Args:
            mode: Selection mode
            input_val: Index (for BY_INDEX mode)
            
        Returns:
            Selected wallet
        """
        if self.max_wallets == 0:
            return None
            
        with self.selection_lock:
            if mode == WalletSelectionMode.BY_INDEX:
                idx = input_val % self.max_wallets
                return self.wallets[idx]
            elif mode == WalletSelectionMode.RANDOM:
                idx = random.randint(0, self.max_wallets - 1)
                return self.wallets[idx]
            elif mode == WalletSelectionMode.ROUND_ROBIN:
                idx = self.rr_wallet_idx
                self.rr_wallet_idx = (self.rr_wallet_idx + 1) % self.max_wallets
                return self.wallets[idx]
        
        return None
    
    def get_client(self, mode: ClientSelectionMode, input_val: int = 0) -> Optional[Client]:
        """
        Get a client using the specified selection mode.
        
        Args:
            mode: Selection mode
            input_val: Index (for BY_INDEX mode)
            
        Returns:
            Selected client
        """
        if not self.clients:
            return None
            
        with self.selection_lock:
            if mode == ClientSelectionMode.BY_INDEX:
                idx = input_val % len(self.clients)
                return self.clients[idx]
            elif mode == ClientSelectionMode.RANDOM:
                idx = random.randint(0, len(self.clients) - 1)
                return self.clients[idx]
            elif mode == ClientSelectionMode.ROUND_ROBIN:
                idx = self.rr_client_idx
                self.rr_client_idx = (self.rr_client_idx + 1) % len(self.clients)
                return self.clients[idx]
        
        return None 
    
    def get_strategy(self, mode: StrategySelectionMode, input_val: int = 0) -> Optional[Client]:
        """
        Get a strategy using the specified selection mode.
        
        Args:
            mode: Selection mode
            input_val: Index (for BY_INDEX mode)
            
        Returns:
            Selected strategy
        """
        if not self.strategies:
            return None
            
        with self.selection_lock:
            if mode == StrategySelectionMode.BY_INDEX:
                idx = input_val % len(self.strategies)
                return self.strategies[idx]
            elif mode == StrategySelectionMode.RANDOM:
                idx = random.randint(0, len(self.strategies) - 1)
                return self.strategies[idx]
            elif mode == StrategySelectionMode.ROUND_ROBIN:
                idx = self.rr_strategy_idx
                self.rr_strategy_idx = (self.rr_strategy_idx + 1) % len(self.strategies)
                return self.strategies[idx]
        
        return None 