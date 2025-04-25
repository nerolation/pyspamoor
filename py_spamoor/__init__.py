"""py_spamoor - Ethereum transaction automation tool."""

from py_spamoor.wallet import Wallet
from py_spamoor.client import Client, ClientConfig
from py_spamoor.wallet_pool import (
    WalletPool, WalletSelectionMode, ClientSelectionMode, 
    StrategySelectionMode, Strategy
)

__version__ = "0.1.0"
__all__ = [
    "Wallet", 
    "Client", 
    "ClientConfig", 
    "WalletPool", 
    "WalletSelectionMode", 
    "ClientSelectionMode",
    "StrategySelectionMode",
    "Strategy"
] 