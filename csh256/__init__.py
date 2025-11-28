"""
CSH-256: Custom Secure Hash - 256 bit
A hybrid password hashing algorithm with time-cost resistance

Author: Ibrahim Hilal Aboukila
License: MIT
"""

import os
import secrets
from typing import Optional, Union, Dict
from ._version import __version__

# Try to import C extension, fallback to pure Python
try:
    from . import _csh256 as _backend
    _USE_C_BACKEND = True
except ImportError:
    from . import core as _backend
    _USE_C_BACKEND = False
    import warnings
    warnings.warn(
        "C extension not available, using pure Python implementation. "
        "Performance will be significantly slower.",
        RuntimeWarning
    )

from .utils import generate_salt, format_phc_string, parse_phc_string

# Default configuration
DEFAULT_ITERATIONS = 4096
DEFAULT_SALT_SIZE = 16
MIN_ITERATIONS = 64

__all__ = [
    'hash',
    'hash_full',
    'verify',
    'generate_salt',
    'format_hash',
    'parse_hash',
    '__version__',
    'get_backend'
]


def hash(password: Union[str, bytes],
         salt: Optional[bytes] = None,
         iterations: Optional[int] = None) -> str:
    """
    Generate a CSH-256 hash of the password.
    
    This is the simplest interface - it generates a hash and returns it as
    a hex string. Salt and iterations are optional; if not provided, secure
    defaults are used.
    
    Args:
        password: The password to hash (string or bytes)
        salt: Optional 16-byte salt. If None, a random salt is generated.
        iterations: Optional iteration count. If None, uses DEFAULT_ITERATIONS (4096).
    
    Returns:
        64-character hexadecimal hash string
    
    Example:
        >>> import csh256
        >>> hash_value = csh256.hash("my_password")
        >>> print(hash_value)
        'a3f2b1c4...'
    
    Note:
        If you need to store the hash for later verification, use hash_full()
        instead, which returns the salt and iterations along with the hash.
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    if salt is None:
        salt = generate_salt()
    
    if iterations is None:
        iterations = DEFAULT_ITERATIONS
    
    if len(salt) != DEFAULT_SALT_SIZE:
        raise ValueError(f"Salt must be exactly {DEFAULT_SALT_SIZE} bytes")
    
    if iterations < MIN_ITERATIONS:
        raise ValueError(f"Iterations must be at least {MIN_ITERATIONS}")
    
    return _backend.hash(password, salt, iterations)


def hash_full(password: Union[str, bytes],
              salt: Optional[bytes] = None,
              iterations: Optional[int] = None) -> Dict[str, Union[str, bytes, int]]:
    """
    Generate a complete CSH-256 hash with all parameters.
    
    This function returns a dictionary containing the hash, salt, and iteration
    count. This is ideal for storing in databases or when you need all components.
    
    Args:
        password: The password to hash (string or bytes)
        salt: Optional 16-byte salt. If None, a random salt is generated.
        iterations: Optional iteration count. If None, uses DEFAULT_ITERATIONS (4096).
    
    Returns:
        Dictionary with keys:
            - 'hash': 64-character hexadecimal hash string
            - 'salt': 16-byte salt value
            - 'iterations': iteration count used
            - 'formatted': PHC-formatted string (ready to store)
    
    Example:
        >>> import csh256
        >>> result = csh256.hash_full("my_password")
        >>> print(result['hash'])
        'a3f2b1c4...'
        >>> print(result['salt'].hex())
        '3f4e2a...'
        >>> print(result['iterations'])
        4096
        >>> # Store result['formatted'] in your database
        >>> db.store(username, result['formatted'])
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    if salt is None:
        salt = generate_salt()
    
    if iterations is None:
        iterations = DEFAULT_ITERATIONS
    
    if len(salt) != DEFAULT_SALT_SIZE:
        raise ValueError(f"Salt must be exactly {DEFAULT_SALT_SIZE} bytes")
    
    if iterations < MIN_ITERATIONS:
        raise ValueError(f"Iterations must be at least {MIN_ITERATIONS}")
    
    hash_value = _backend.hash(password, salt, iterations)
    formatted = format_phc_string(hash_value, salt, iterations)
    
    return {
        'hash': hash_value,
        'salt': salt,
        'iterations': iterations,
        'formatted': formatted
    }


def verify(password: Union[str, bytes],
           hash_value: Optional[str] = None,
           salt: Optional[bytes] = None,
           iterations: Optional[int] = None,
           formatted: Optional[str] = None) -> bool:
    """
    Verify a password against a stored hash.
    
    You can verify either by providing the individual components (hash, salt,
    iterations) OR by providing a PHC-formatted string.
    
    Args:
        password: The password to verify
        hash_value: The stored hash (64-char hex string)
        salt: The stored salt (16 bytes)
        iterations: The stored iteration count
        formatted: Alternative: PHC-formatted string containing all components
    
    Returns:
        True if password matches, False otherwise
    
    Examples:
        >>> # Verify with individual components
        >>> is_valid = csh256.verify("password", hash_value, salt, iterations)
        
        >>> # Verify with formatted string
        >>> stored = "$csh256$i=4096$salt$hash"
        >>> is_valid = csh256.verify("password", formatted=stored)
    
    Raises:
        ValueError: If neither individual components nor formatted string provided
    """
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Parse formatted string if provided
    if formatted is not None:
        try:
            parsed = parse_phc_string(formatted)
            hash_value = parsed['hash']
            salt = parsed['salt']
            iterations = parsed['iterations']
        except Exception as e:
            raise ValueError(f"Invalid formatted hash string: {e}")
    
    # Validate we have all required components
    if hash_value is None or salt is None or iterations is None:
        raise ValueError(
            "Must provide either (hash_value, salt, iterations) or formatted string"
        )
    
    # Compute hash with same parameters
    computed_hash = _backend.hash(password, salt, iterations)
    
    # Constant-time comparison
    return secrets.compare_digest(computed_hash, hash_value)


def format_hash(hash_value: str, salt: bytes, iterations: int) -> str:
    """
    Format hash components into PHC string format.
    
    PHC (Password Hashing Competition) string format is a standardized way
    to store password hashes with their parameters.
    
    Format: $csh256$i=<iterations>$<salt_base64>$<hash>
    
    Args:
        hash_value: 64-character hexadecimal hash
        salt: 16-byte salt
        iterations: iteration count
    
    Returns:
        PHC-formatted string
    
    Example:
        >>> formatted = csh256.format_hash(hash_val, salt, 4096)
        >>> print(formatted)
        '$csh256$i=4096$3f4e2a1b...$a3f2b1c4...'
    """
    return format_phc_string(hash_value, salt, iterations)


def parse_hash(formatted: str) -> Dict[str, Union[str, bytes, int]]:
    """
    Parse a PHC-formatted hash string into components.
    
    Args:
        formatted: PHC-formatted string
    
    Returns:
        Dictionary with keys: 'hash', 'salt', 'iterations'
    
    Example:
        >>> formatted = "$csh256$i=4096$3f4e2a...$a3f2b1..."
        >>> components = csh256.parse_hash(formatted)
        >>> print(components['iterations'])
        4096
    """
    return parse_phc_string(formatted)


def get_backend() -> str:
    """
    Get the name of the backend implementation being used.
    
    Returns:
        'C' if using C extension, 'Python' if using pure Python fallback
    
    Example:
        >>> print(csh256.get_backend())
        'C'
    """
    return 'C' if _USE_C_BACKEND else 'Python'


# Convenience: Allow importing specific functions
def get_default_iterations() -> int:
    """Get the default iteration count."""
    return DEFAULT_ITERATIONS


def set_default_iterations(iterations: int) -> None:
    """
    Set the default iteration count for future hash() calls.
    
    Args:
        iterations: New default iteration count (must be >= 64)
    
    Example:
        >>> csh256.set_default_iterations(8192)  # Increase security
    """
    global DEFAULT_ITERATIONS
    if iterations < MIN_ITERATIONS:
        raise ValueError(f"Iterations must be at least {MIN_ITERATIONS}")
    DEFAULT_ITERATIONS = iterations