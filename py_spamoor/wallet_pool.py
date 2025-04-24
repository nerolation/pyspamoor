"""
Wallet pool management for py_spamoor.
"""
import os
import random
import enum
import threading
from typing import List, Dict, Optional

from py_spamoor.wallet import Wallet
from py_spamoor.client import Client


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


class WalletPool:
    """Pool of wallets with various selection methods."""
    
    def __init__(self, clients: List[Client]):
        """
        Initialize wallet pool.
        
        Args:
            clients: List of available clients
        """
        self.clients = clients
        self.wallets: List[Wallet] = []
        self.wallet_names: Dict[str, str] = {}  # address -> name mapping
        
        # State for selection modes
        self.max_wallets = 0
        self.rr_wallet_idx = 0
        self.rr_client_idx = 0
        self.selection_lock = threading.Lock()
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load private keys from a file.
        
        Args:
            file_path: Path to file containing private keys (one per line)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Private key file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            keys = [line.strip() for line in f.readlines()]
        
        # Filter out empty lines and comments
        keys = [key for key in keys if key and not key.startswith('#')]
        
        # Clear existing wallets
        self.wallets = []
        
        # Create wallets
        for i, key in enumerate(keys):
            wallet = Wallet(key)
            self.wallets.append(wallet)
            self.wallet_names[wallet.get_address()] = f"wallet_{i+1}"
        
        self.max_wallets = len(self.wallets)
    
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