import json
import re
from typing import Optional, List, Tuple, Dict

def load_private_keys(file_path="pks.txt"):
    """
    Load private keys from a text file containing a list of dicts.
    Handles cases where the content is not perfectly formatted JSON.
    """
    with open(file_path, "r") as f:
        raw = f.read().strip()

    # Try to extract JSON array using regex (non-greedy match)
    match = re.search(r'\[\s*{.*?}\s*\]', raw, re.DOTALL)
    if not match:
        raise ValueError("Could not find a valid JSON array in the file.")
    
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing error: {e}")

    return data

def parse_el_rpc_endpoints(file_path="rpc.txt"):
    """
    Parses RPC endpoints (8545) for EL containers from a container service list.
    Starts scanning only after finding the first 'el-' container.

    Args:
        file_path (str): Path to the text file with container info.

    Returns:
        Dict[str, str]: Mapping of EL container names to RPC URLs.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    started = False
    container_name = None
    endpoints = {}

    for line in lines:
        # Wait until we see an "el-" container
        if not started:
            if re.search(r"\b(el-\d+-[\w-]+)", line):
                started = True
            else:
                continue

        # Try to match a container name (starts with el-)
        match_container = re.match(r"^\w+\s+(el-[\w-]+)", line)
        if match_container:
            container_name = match_container.group(1)

        # Look for rpc: 8545/tcp -> 127.0.0.1:<port>
        match_rpc = re.search(r"rpc:\s*8545/tcp\s*->\s*127\.0\.0\.1:(\d+)", line)
        if match_rpc and container_name:
            port = match_rpc.group(1)
            endpoints[container_name] = f"http://127.0.0.1:{port}"

    return endpoints

# Constants for EIP-4844 blobs
# BLS12-381 field modulus
BLS_MODULUS = int(
    "73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001", 16
)
BYTES_PER_FIELD_ELEMENT = 32
FIELD_ELEMENTS_PER_BLOB = 4096

def prepare_blob(data: Optional[bytes] = None) -> bytes:
    """
    Create a single EIP-4844 blob:
    - If `data` is provided (bytes or str), it is chunked, padded, and verified against the BLS modulus.
    - Otherwise, each field element is a random integer < BLS_MODULUS.

    Returns the blob as concatenated bytes of length 32 * 4096.
    """
    field_elements: List[bytes] = []

    if data is not None:
        # Allow passing in a string
        if isinstance(data, str):
            data = data.encode()
        # Split into 32-byte chunks
        for i in range(0, len(data), BYTES_PER_FIELD_ELEMENT):
            chunk = data[i : i + BYTES_PER_FIELD_ELEMENT]
            # Pad chunk to exactly 32 bytes
            chunk = chunk.ljust(BYTES_PER_FIELD_ELEMENT, b"\x00")
            # Ensure it is within the field
            if int.from_bytes(chunk, "big") >= BLS_MODULUS:
                raise ValueError("Chunk value exceeds BLS modulus")
            field_elements.append(chunk)
    else:
        # Generate random field elements
        for _ in range(FIELD_ELEMENTS_PER_BLOB):
            rand_int = secrets.randbelow(BLS_MODULUS)
            field_elements.append(rand_int.to_bytes(BYTES_PER_FIELD_ELEMENT, "big"))

    # Pad with zero-elements if needed
    zero_elem = (0).to_bytes(BYTES_PER_FIELD_ELEMENT, "big")
    while len(field_elements) < FIELD_ELEMENTS_PER_BLOB:
        field_elements.append(zero_elem)

    # Concatenate all field elements into a single blob
    return b"".join(field_elements)

def generate_random_blobs(count: int) -> List[bytes]:
    """
    Generate `count` random blobs (each 4096 * 32 bytes).
    """
    return [prepare_blob() for _ in range(count)]

def prepare_access_list(
    entries: Optional[List[Tuple[str, List[str]]]] = None,
) -> List[Dict[str, List[str]]]:
    """
    Create an EIP-2930 access list.

    :param entries: List of tuples (address, list of storage keys [hex strings]).
    :return:        Access list suitable for tx dict "accessList" field.
    """
    access_list: List[Dict[str, List[str]]] = []
    if not entries:
        return access_list

    for addr, keys in entries:
        storage_keys: List[str] = []
        for key in keys:
            hex_key = key if key.startswith("0x") else f"0x{key}"
            if len(hex_key) != 66:
                raise ValueError(f"Invalid storage key length: {hex_key}")
            storage_keys.append(hex_key)
        access_list.append({
            "address": addr,
            "storageKeys": storage_keys
        })
    return access_list

def generate_random_access_list(
    count: int,
    keys_per_address: int,
) -> List[Dict[str, List[str]]]:
    """
    Generate a random access list for testing:
    - `count` random addresses, each with `keys_per_address` random storage keys.
    """
    access_list: List[Dict[str, List[str]]] = []
    for _ in range(count):
        addr = f"0x{secrets.token_hex(20)}"
        storage_keys = [f"0x{secrets.token_hex(32)}" for _ in range(keys_per_address)]
        access_list.append({
            "address": addr,
            "storageKeys": storage_keys
        })
    return access_list

def generate_zero_bytes(size_all_zeros):
    return b'\x00' * size_all_zeros

def generate_nonzero_bytes(size_all_nonzeros):
    return bytes(random.choices(range(1, 256), k=size_all_nonzeros))

def generate_mixed_bytes(num_zero_bytes, num_nonzero_bytes):
    zero_part = b'\x00' * num_zero_bytes
    nonzero_part = bytes(random.choices(range(1, 256), k=num_nonzero_bytes))
    mixed_data = bytearray(zero_part + nonzero_part)
    mixed_data_list = list(mixed_data)
    random.shuffle(mixed_data_list)
    return bytes(mixed_data_list)


BASE_COST = 21_000
COST_CALLDATA_ZEROS = 10
COST_CALLDATA_NONZEROS = 40
def get_max_calldata_zeros_for_limit(block_gas_limit):
    return (block_gas_limit - BASE_COST) // COST_CALLDATA_ZEROS

def get_max_calldata_nonzeros_for_limit(block_gas_limit):
    return (block_gas_limit - BASE_COST) // COST_CALLDATA_NONZEROS

def get_max_calldata_mix_for_limit(block_gas_limit):
    available_gas = block_gas_limit - BASE_COST
    nonzero_gas = int(available_gas * 71 / 100)
    zero_gas = available_gas - nonzero_gas
    
    num_nonzeros = nonzero_gas // COST_CALLDATA_NONZEROS
    num_zeros = zero_gas // COST_CALLDATA_ZEROS
    return num_nonzeros, num_zeros
