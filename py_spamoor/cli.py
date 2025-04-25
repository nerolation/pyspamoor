#!/usr/bin/env python3
"""
Command-line interface for py_spamoor - Ethereum transaction spammer
"""
import os
import time
import sys
import argparse
import random
import logging
import json
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.logging import RichHandler

from py_spamoor.wallet import Wallet
from py_spamoor.wallet_pool import (
    WalletPool, Strategy, WalletSelectionMode, 
    ClientSelectionMode, StrategySelectionMode
)
from py_spamoor.client import Client, ClientConfig
from py_spamoor.helper import (
    load_private_keys, parse_el_rpc_endpoints, 
    get_max_calldata_zeros_for_limit, generate_zero_bytes,
    generate_nonzero_bytes, generate_mixed_bytes,
    prepare_access_list, generate_random_access_list,
    prepare_blob, get_max_calldata_nonzeros_for_limit, 
    get_max_calldata_mix_for_limit, get_max_access_list_for_limit,
    generate_random_blobs
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("spamoor")
console = Console()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ethereum Transaction Spammer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # File paths
    parser.add_argument(
        "--private-keys-file", "-k",
        help="Path to file containing private keys",
        default="pks.txt"
    )
    parser.add_argument(
        "--rpc-file", "-r",
        help="Path to file containing RPC endpoints",
        default="rpc.txt"
    )
    
    # Chain configuration
    parser.add_argument(
        "--chain-id", "-c",
        help="Chain ID for transactions",
        type=int,
        default=3151908
    )
    
    # Selection modes
    parser.add_argument(
        "--wallet-selection", "-w",
        help="Wallet selection mode",
        choices=["index", "random", "round-robin"],
        default="round-robin"
    )
    parser.add_argument(
        "--client-selection", "-n",
        help="Client selection mode",
        choices=["index", "random", "round-robin"],
        default="round-robin"
    )
    parser.add_argument(
        "--strategy-selection", "-s",
        help="Strategy selection mode",
        choices=["index", "random", "round-robin"],
        default="round-robin"
    )
    
    # Transaction strategies
    parser.add_argument(
        "--strategies",
        help="Transaction strategies to use (comma-separated)",
        default="standard-tx,calldata-zeros"
    )
    
    # Transaction parameters
    parser.add_argument(
        "--gas-limit",
        help="Gas limit for transactions (will use block limit if not specified)",
        type=int
    )
    parser.add_argument(
        "--max-fee-per-gas",
        help="Max fee per gas (wei)",
        type=int,
        default=1000000000
    )
    parser.add_argument(
        "--max-priority-fee-per-gas",
        help="Max priority fee per gas (wei)",
        type=int,
        default=1000000000
    )
    parser.add_argument(
        "--max-fee-per-blob-gas",
        help="Max fee per blob gas (wei, for blob transactions)",
        type=int,
        default=1000000000
    )
    
    # Rate limiting
    parser.add_argument(
        "--tx-delay",
        help="Delay between transactions (seconds)",
        type=float,
        default=1.0
    )
    parser.add_argument(
        "--tx-count",
        help="Number of transactions to send (0 for unlimited)",
        type=int,
        default=0
    )
    
    # Debugging/verbosity
    parser.add_argument(
        "--verbose", "-v",
        help="Increase output verbosity",
        action="store_true"
    )
    parser.add_argument(
        "--dry-run",
        help="Don't send transactions, just print them",
        action="store_true"
    )
    
    return parser.parse_args()

def get_selection_mode(mode_str: str, selection_type: str) -> Any:
    """Convert string selection mode to enum value."""
    if selection_type == "wallet":
        if mode_str == "index":
            return WalletSelectionMode.BY_INDEX
        elif mode_str == "random":
            return WalletSelectionMode.RANDOM
        else:
            return WalletSelectionMode.ROUND_ROBIN
            
    elif selection_type == "client":
        if mode_str == "index":
            return ClientSelectionMode.BY_INDEX
        elif mode_str == "random":
            return ClientSelectionMode.RANDOM
        else:
            return ClientSelectionMode.ROUND_ROBIN
            
    elif selection_type == "strategy":
        if mode_str == "index":
            return StrategySelectionMode.BY_INDEX
        elif mode_str == "random":
            return StrategySelectionMode.RANDOM
        else:
            return StrategySelectionMode.ROUND_ROBIN
            
    raise ValueError(f"Unknown selection type: {selection_type}")

def get_strategies_from_string(strategy_str: str) -> List[Strategy]:
    """Convert comma-separated strategy string to list of Strategy enums."""
    strategies = []
    for s in strategy_str.split(","):
        s = s.strip().lower()
        if s == "standard-tx":
            strategies.append(Strategy.STANDARD_TX)
        elif s == "calldata-zeros":
            strategies.append(Strategy.CALLDATA_ZEROS)
        elif s == "calldata-non-zeros":
            strategies.append(Strategy.CALLDATA_NON_ZEROS)
        elif s == "calldata-mix":
            strategies.append(Strategy.CALLDATA_MIX)
        elif s == "access-list":
            strategies.append(Strategy.ACCESS_LIST)
        elif s == "blobs":
            strategies.append(Strategy.BLOBS)
        else:
            logger.warning(f"Unknown strategy: {s}")
            
    return strategies

def prompt_for_file(prompt_text: str, default_path: str) -> str:
    """Prompt user for file path if it doesn't exist."""
    path = default_path
    while not os.path.exists(path):
        user_input = input(f"{prompt_text} (default: {default_path}): ").strip()
        if user_input:
            path = user_input
        else:
            print(f"File not found: {path}")
    return path

def setup_wallet_pool(args) -> WalletPool:
    """Setup and configure the wallet pool."""
    pool = WalletPool()
    
    # Private keys file
    pk_file = args.private_keys_file
    if not os.path.exists(pk_file):
        pk_file = prompt_for_file("Enter private keys file path", pk_file)
    
    console.print(f"[bold green]Loading private keys from:[/] {pk_file}")
    pool.load_private_key_from_file(pk_file)
    
    # RPC endpoints file
    rpc_file = args.rpc_file
    if not os.path.exists(rpc_file):
        rpc_file = prompt_for_file("Enter RPC endpoints file path", rpc_file)
        
    console.print(f"[bold green]Loading RPC endpoints from:[/] {rpc_file}")
    pool.load_clients_from_file(rpc_file)
    
    # Strategies
    strategies = get_strategies_from_string(args.strategies)
    console.print(f"[bold green]Using strategies:[/] {', '.join(s.name for s in strategies)}")
    pool.add_strategy(strategies)
    
    return pool

def display_configuration(args, pool: WalletPool):
    """Display configuration table."""
    table = Table(title="Spamoor Configuration")
    
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Chain ID", str(args.chain_id))
    table.add_row("Wallet Selection Mode", args.wallet_selection)
    table.add_row("Client Selection Mode", args.client_selection)
    table.add_row("Strategy Selection Mode", args.strategy_selection)
    table.add_row("Max Fee Per Gas", f"{args.max_fee_per_gas} wei")
    table.add_row("Max Priority Fee Per Gas", f"{args.max_priority_fee_per_gas} wei")
    
    if args.gas_limit:
        table.add_row("Gas Limit", str(args.gas_limit))
    else:
        table.add_row("Gas Limit", "Auto (block limit)")
    
    table.add_row("Transaction Delay", f"{args.tx_delay} seconds")
    
    if args.tx_count > 0:
        table.add_row("Transaction Count", str(args.tx_count))
    else:
        table.add_row("Transaction Count", "Unlimited")
        
    table.add_row("Wallets Loaded", str(len(pool.wallets)))
    table.add_row("Clients Loaded", str(len(pool.clients)))
    table.add_row("Strategies Loaded", str(len(pool.strategies)))
    
    table.add_row("Dry Run", "Yes" if args.dry_run else "No")
    
    console.print(table)

def handle_standard_tx(client: Client, wallet: Wallet, args) -> Dict[str, Any]:
    """Handle standard transaction strategy."""
    return wallet.build_transaction(
        wallet.get_address(),
        chain_id=args.chain_id,
        max_fee_per_gas=args.max_fee_per_gas,
        max_priority_fee_per_gas=args.max_priority_fee_per_gas
    )

def handle_calldata_zeros(client: Client, wallet: Wallet, args) -> Dict[str, Any]:
    """Handle calldata zeros strategy."""
    block_gas_limit = client.block_gas_limit
    gas_limit = args.gas_limit if args.gas_limit else block_gas_limit
    calldata_zeros = get_max_calldata_zeros_for_limit(gas_limit)
    data = generate_zero_bytes(calldata_zeros)
    
    return wallet.build_transaction(
        wallet.get_address(),
        chain_id=args.chain_id,
        gas=gas_limit,
        max_fee_per_gas=args.max_fee_per_gas,
        max_priority_fee_per_gas=args.max_priority_fee_per_gas,
        data=data
    )

def handle_calldata_non_zeros(client: Client, wallet: Wallet, args) -> Dict[str, Any]:
    """Handle calldata non-zeros strategy."""
    block_gas_limit = client.block_gas_limit
    gas_limit = args.gas_limit if args.gas_limit else block_gas_limit
    max_non_zeros = get_max_calldata_nonzeros_for_limit(gas_limit)
    data = generate_nonzero_bytes(max_non_zeros)
    
    return wallet.build_transaction(
        wallet.get_address(),
        chain_id=args.chain_id,
        gas=gas_limit,
        max_fee_per_gas=args.max_fee_per_gas,
        max_priority_fee_per_gas=args.max_priority_fee_per_gas,
        data=data
    )

def handle_calldata_mix(client: Client, wallet: Wallet, args) -> Dict[str, Any]:
    """Handle mixed calldata strategy."""
    block_gas_limit = client.block_gas_limit
    gas_limit = args.gas_limit if args.gas_limit else block_gas_limit
    
    # Use 60% of available gas for non-zeros, 40% for zeros
    num_nonzeros, num_zeros = get_max_calldata_mix_for_limit(gas_limit)
    
    data = generate_mixed_bytes(num_zeros, num_nonzeros)
    
    return wallet.build_transaction(
        wallet.get_address(),
        chain_id=args.chain_id,
        gas=gas_limit,
        max_fee_per_gas=args.max_fee_per_gas,
        max_priority_fee_per_gas=args.max_priority_fee_per_gas,
        data=data
    )

def handle_access_list(client: Client, wallet: Wallet, args) -> Dict[str, Any]:
    """Handle access list strategy."""
    block_gas_limit = client.block_gas_limit
    gas_limit = args.gas_limit if args.gas_limit else block_gas_limit
    access_list = generate_random_access_list(
        1,
        get_max_access_list_for_limit(gas_limit), 
    )
    
    return wallet.build_transaction(
        wallet.get_address(),
        chain_id=args.chain_id,
        max_fee_per_gas=args.max_fee_per_gas,
        max_priority_fee_per_gas=args.max_priority_fee_per_gas,
        accessList=access_list
    )

def handle_blobs(client: Client, wallet: Wallet, args) -> Dict[str, Any]:
    """Handle blob transaction strategy."""
    # Generate a single random blob
    blob_data = generate_random_blobs(6)
    
    return wallet.build_transaction(
        wallet.get_address(),
        chain_id=args.chain_id,
        max_fee_per_gas=args.max_fee_per_gas,
        max_priority_fee_per_gas=args.max_priority_fee_per_gas,
        max_fee_per_blob_gas=args.max_fee_per_blob_gas,
        blob_data=blob_data
    )

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Setup wallet pool
        pool = setup_wallet_pool(args)
        
        # Display configuration
        display_configuration(args, pool)
        
        # Get selection modes
        wallet_mode = get_selection_mode(args.wallet_selection, "wallet")
        client_mode = get_selection_mode(args.client_selection, "client")
        strategy_mode = get_selection_mode(args.strategy_selection, "strategy")
        
        # Create generator functions
        clients_gen = lambda: pool.get_client(client_mode)
        wallet_gen = lambda: pool.get_wallet(wallet_mode)
        strategies_gen = lambda: pool.get_strategy(strategy_mode)
        
        # Strategy handler mapping
        strategy_handlers = {
            Strategy.STANDARD_TX: handle_standard_tx,
            Strategy.CALLDATA_ZEROS: handle_calldata_zeros,
            Strategy.CALLDATA_NON_ZEROS: handle_calldata_non_zeros,
            Strategy.CALLDATA_MIX: handle_calldata_mix,
            Strategy.ACCESS_LIST: handle_access_list,
            Strategy.BLOBS: handle_blobs
        }
        
        # Ask for confirmation
        if not args.dry_run:
            confirm = input("Ready to start spamming transactions. Continue? [y/N]: ")
            if confirm.lower() != 'y':
                console.print("[bold red]Aborting.[/]")
                return
        
        # Initialize progress tracking
        tx_count = args.tx_count if args.tx_count > 0 else None
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Sending transactions...", total=tx_count)
            
            tx_sent = 0
            while True:
                if tx_count and tx_sent >= tx_count:
                    break
                    
                client = clients_gen()
                wallet = wallet_gen()
                strategy = strategies_gen()
                
                if not client or not wallet or not strategy:
                    logger.error("Failed to get client, wallet, or strategy. Check configuration.")
                    break
                
                handler = strategy_handlers.get(strategy)
                if not handler:
                    logger.warning(f"No handler for strategy: {strategy}")
                    continue
                
                try:
                    # Build transaction using appropriate handler
                    tx = handler(client, wallet, args)
                    
                    # For dry run, just print the transaction
                    if args.dry_run:
                        console.print(f"[bold green]Transaction built ([strategy.name]):[/]")
                        console.print(json.dumps(tx, indent=2))
                    else:
                        # Sign and send transaction
                        signed_tx = wallet.sign_transaction(tx, client)
                        tx_hash = client.send_transaction(signed_tx)
                        tx_hex = tx_hash.hex()
                        
                        if args.verbose:
                            receipt = client.wait_for_transaction_receipt(tx_hash)
                            console.print(f"[bold green]Transaction sent:[/] {tx_hex}")
                            console.print(f"[bold green]Receipt:[/] {receipt}")
                        else:
                            console.print(f"[bold green]Transaction sent:[/] {tx_hex[:10]}...{tx_hex[-8:]}")
                    
                    tx_sent += 1
                    progress.update(task, advance=1, description=f"[cyan]Sent {tx_sent} transactions")
                    
                    # Sleep between transactions
                    time.sleep(args.tx_delay)
                    
                except Exception as e:
                    logger.error(f"Error processing transaction: {e}")
                    if args.verbose:
                        import traceback
                        traceback.print_exc()
                    time.sleep(args.tx_delay)  # Still sleep on error to avoid rapid retries
        
        console.print(f"[bold green]Completed![/] Sent {tx_sent} transactions.")
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted by user. Exiting...[/]")
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 