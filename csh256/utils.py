"""
Utility functions for CSH-256 library
"""

import secrets
from typing import Dict, Union


DEFAULT_SALT_SIZE = 16


def generate_salt(size: int = DEFAULT_SALT_SIZE) -> bytes:
    """
    Generate a cryptographically secure random salt.
    
    Args:
        size: Size of salt in bytes (default: 16)
    
    Returns:
        Random bytes suitable for use as salt
    
    Example:
        >>> salt = generate_salt()
        >>> len(salt)
        16
        >>> salt = generate_salt(32)  # Custom size
        >>> len(salt)
        32
    """
    return secrets.token_bytes(size)


def format_phc_string(hash_value: str, salt: bytes, iterations: int) -> str:
    """
    Format hash components into PHC (Password Hashing Competition) string format.
    
    Format: $csh256$i=<iterations>$<salt_hex>$<hash>
    
    Args:
        hash_value: 64-character hexadecimal hash
        salt: Salt bytes
        iterations: Iteration count
    
    Returns:
        PHC-formatted string
    
    Example:
        >>> formatted = format_phc_string("a3f2...", b"salt...", 4096)
        >>> print(formatted)
        '$csh256$i=4096$73616c74...$a3f2...'
    """
    salt_hex = salt.hex()
    return f"$csh256$i={iterations}${salt_hex}${hash_value}"


def parse_phc_string(formatted: str) -> Dict[str, Union[str, bytes, int]]:
    """
    Parse a PHC-formatted string into its components.
    
    Args:
        formatted: PHC-formatted string
    
    Returns:
        Dictionary with keys:
            - 'hash': hash value (hex string)
            - 'salt': salt (bytes)
            - 'iterations': iteration count (int)
    
    Raises:
        ValueError: If format is invalid
    
    Example:
        >>> formatted = "$csh256$i=4096$73616c74...$a3f2..."
        >>> components = parse_phc_string(formatted)
        >>> components['iterations']
        4096
    """
    parts = formatted.split('$')
    
    # Format should be: ['', 'csh256', 'i=XXXX', 'salt_hex', 'hash']
    if len(parts) != 5:
        raise ValueError(f"Invalid PHC format: expected 5 parts, got {len(parts)}")
    
    if parts[0] != '' or parts[1] != 'csh256':
        raise ValueError("Invalid PHC format: must start with '$csh256$'")
    
    # Parse iterations
    if not parts[2].startswith('i='):
        raise ValueError("Invalid PHC format: iterations must be 'i=XXXX'")
    
    try:
        iterations = int(parts[2][2:])
    except ValueError:
        raise ValueError(f"Invalid iteration count: {parts[2][2:]}")
    
    # Parse salt (hex encoded)
    try:
        salt = bytes.fromhex(parts[3])
    except ValueError:
        raise ValueError("Invalid salt: must be hex-encoded")
    
    # Hash is already in hex format
    hash_value = parts[4]
    
    if len(hash_value) != 64:
        raise ValueError(f"Invalid hash length: expected 64 characters, got {len(hash_value)}")
    
    return {
        'hash': hash_value,
        'salt': salt,
        'iterations': iterations
    }


def hex_to_bytes(hex_string: str) -> bytes:
    """
    Convert hex string to bytes.
    
    Args:
        hex_string: Hexadecimal string
    
    Returns:
        Bytes representation
    """
    return bytes.fromhex(hex_string)


def bytes_to_hex(data: bytes) -> str:
    """
    Convert bytes to hex string.
    
    Args:
        data: Bytes to convert
    
    Returns:
        Hexadecimal string (lowercase)
    """
    return data.hex()


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time.
    
    This prevents timing attacks by ensuring comparison
    always takes the same amount of time regardless of
    where the strings differ.
    
    Args:
        a: First string
        b: Second string
    
    Returns:
        True if strings are equal, False otherwise
    """
    return secrets.compare_digest(a, b)


def estimate_hash_time(iterations: int, sample_iterations: int = 100) -> float:
    """
    Estimate how long it will take to compute a hash with given iterations.
    
    This performs a small benchmark to estimate the time cost.
    
    Args:
        iterations: Target iteration count
        sample_iterations: Number of iterations to use for benchmark
    
    Returns:
        Estimated time in seconds
    
    Note:
        This is an approximation. Actual time may vary based on
        system load and other factors.
    """
    import time
    
    # Import here to avoid circular dependency
    from . import hash as csh_hash
    
    test_password = b"benchmark_password_123"
    test_salt = generate_salt()
    
    # Benchmark with sample iterations
    start = time.perf_counter()
    csh_hash(test_password, salt=test_salt, iterations=sample_iterations)
    elapsed = time.perf_counter() - start
    
    # Extrapolate to target iterations
    time_per_iteration = elapsed / sample_iterations
    estimated_time = time_per_iteration * iterations
    
    return estimated_time


def recommend_iterations(target_time_ms: float = 250) -> int:
    """
    Recommend an iteration count based on target computation time.
    
    This benchmarks the system and suggests an iteration count
    that will result in approximately the target time.
    
    Args:
        target_time_ms: Target time in milliseconds (default: 250ms)
    
    Returns:
        Recommended iteration count
    
    Example:
        >>> # Find iterations for ~500ms computation time
        >>> iterations = recommend_iterations(500)
        >>> print(f"Use {iterations} iterations")
        Use 8192 iterations
    """
    target_time_sec = target_time_ms / 1000.0
    
    # Start with a small benchmark
    sample_iterations = 100
    sample_time = estimate_hash_time(sample_iterations, sample_iterations)
    
    # Calculate recommended iterations
    time_per_iteration = sample_time / sample_iterations
    recommended = int(target_time_sec / time_per_iteration)
    
    # Round to nearest power of 2 for cleaner numbers
    import math
    recommended = 2 ** round(math.log2(recommended))
    
    # Ensure minimum
    return max(recommended, 64)


def validate_password_strength(password: str, min_length: int = 8) -> Dict[str, Union[bool, str]]:
    """
    Perform basic password strength validation.
    
    This is a helper function for applications using CSH-256.
    It checks common password requirements.
    
    Args:
        password: Password to validate
        min_length: Minimum required length
    
    Returns:
        Dictionary with keys:
            - 'valid': True if password meets requirements
            - 'message': Description of validation result
            - 'score': Strength score (0-5)
    
    Example:
        >>> result = validate_password_strength("MyP@ssw0rd")
        >>> print(result['valid'])
        True
        >>> print(result['score'])
        5
    """
    score = 0
    issues = []
    
    # Length check
    if len(password) < min_length:
        issues.append(f"must be at least {min_length} characters")
    else:
        score += 1
    
    # Complexity checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if has_lower:
        score += 1
    else:
        issues.append("should contain lowercase letters")
    
    if has_upper:
        score += 1
    else:
        issues.append("should contain uppercase letters")
    
    if has_digit:
        score += 1
    else:
        issues.append("should contain numbers")
    
    if has_special:
        score += 1
    else:
        issues.append("should contain special characters")
    
    valid = len(issues) == 0
    
    if valid:
        message = "Strong password"
    else:
        message = "Weak password: " + ", ".join(issues)
    
    return {
        'valid': valid,
        'message': message,
        'score': score
    }