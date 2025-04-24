"""
Rate limiting functionality for py_spamoor.
"""
import time
import threading
from functools import wraps
from typing import Callable, Union

def rate_limited(calls_per_second: Union[float, Callable[..., float]]):
    """
    Decorator to rate limit a function call to a maximum number of calls per second.
    
    Args:
        calls_per_second: Maximum number of calls per second, or a function that returns this value
        
    Returns:
        Decorated function
    """
    min_interval = 1.0  # Default to 1 call per second
    lock = threading.Lock()
    last_call_time = 0.0
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal min_interval, last_call_time
            
            # Get the current rate limit setting
            if callable(calls_per_second):
                current_rate = calls_per_second(*args)
            else:
                current_rate = calls_per_second
                
            # Calculate minimum interval between calls
            if current_rate > 0:
                min_interval = 1.0 / current_rate
            else:
                min_interval = 0  # No rate limiting
                
            # Apply rate limiting
            with lock:
                elapsed = time.time() - last_call_time
                
                # If we need to wait
                if min_interval > 0 and elapsed < min_interval:
                    wait_time = min_interval - elapsed
                    time.sleep(wait_time)
                    
                # Update last call time
                last_call_time = time.time()
                
            # Call the function
            return func(*args, **kwargs)
            
        return wrapper
        
    return decorator 