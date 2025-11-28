"""
Basic usage examples for CSH-256
"""

import csh256

def example_1_simple_hash():
    """Example 1: Simplest usage"""
    print("=" * 60)
    print("Example 1: Simple Hash")
    print("=" * 60)
    
    password = "my_secure_password_123"
    hash_value = csh256.hash(password)
    
    print(f"Password: {password}")
    print(f"Hash: {hash_value}")
    print()


def example_2_complete_hash():
    """Example 2: Get all hash components"""
    print("=" * 60)
    print("Example 2: Complete Hash with All Components")
    print("=" * 60)
    
    password = "another_password"
    result = csh256.hash_full(password)
    
    print(f"Password: {password}")
    print(f"Hash: {result['hash']}")
    print(f"Salt (hex): {result['salt'].hex()}")
    print(f"Iterations: {result['iterations']}")
    print(f"Formatted: {result['formatted']}")
    print()


def example_3_verify():
    """Example 3: Password verification"""
    print("=" * 60)
    print("Example 3: Password Verification")
    print("=" * 60)
    
    # Create a hash
    password = "test_password"
    result = csh256.hash_full(password)
    print(f"Original password: {password}")
    print(f"Hash stored: {result['formatted']}")
    print()
    
    # Verify correct password
    is_valid = csh256.verify(password, formatted=result['formatted'])
    print(f"Verifying '{password}': {is_valid}")
    
    # Verify wrong password
    wrong = "wrong_password"
    is_valid = csh256.verify(wrong, formatted=result['formatted'])
    print(f"Verifying '{wrong}': {is_valid}")
    print()


def example_4_custom_iterations():
    """Example 4: Custom iteration count"""
    print("=" * 60)
    print("Example 4: Custom Iterations for Higher Security")
    print("=" * 60)
    
    password = "high_security_password"
    
    # Standard security (4096 iterations)
    standard = csh256.hash_full(password, iterations=4096)
    print(f"Standard (4096 iterations): {standard['formatted']}")
    
    # High security (8192 iterations) - takes ~2x longer
    high = csh256.hash_full(password, iterations=8192)
    print(f"High (8192 iterations): {high['formatted']}")
    print()


def example_5_database_simulation():
    """Example 5: Simulated database storage"""
    print("=" * 60)
    print("Example 5: Database Storage Simulation")
    print("=" * 60)
    
    # Simulated user database
    database = {}
    
    # User registration
    username = "alice"
    password = "alice_password_123"
    result = csh256.hash_full(password)
    
    # Store in database (only store the formatted string)
    database[username] = result['formatted']
    print(f"Registered user: {username}")
    print(f"Stored hash: {database[username]}")
    print()
    
    # User login - correct password
    login_username = "alice"
    login_password = "alice_password_123"
    
    if login_username in database:
        stored_hash = database[login_username]
        is_valid = csh256.verify(login_password, formatted=stored_hash)
        print(f"Login attempt - Username: {login_username}, Password: {login_password}")
        print(f"Result: {'✓ Success' if is_valid else '✗ Failed'}")
    print()
    
    # User login - wrong password
    login_password_wrong = "wrong_password"
    if login_username in database:
        stored_hash = database[login_username]
        is_valid = csh256.verify(login_password_wrong, formatted=stored_hash)
        print(f"Login attempt - Username: {login_username}, Password: {login_password_wrong}")
        print(f"Result: {'✓ Success' if is_valid else '✗ Failed'}")
    print()


def example_6_recommend_iterations():
    """Example 6: Get recommended iterations"""
    print("=" * 60)
    print("Example 6: Recommended Iterations Based on Target Time")
    print("=" * 60)
    
    # Find iterations for different time targets
    targets = [100, 250, 500, 1000]
    
    print("Finding optimal iterations for different time targets...")
    print()
    
    for target_ms in targets:
        recommended = csh256.recommend_iterations(target_ms)
        print(f"Target: {target_ms}ms → Recommended iterations: {recommended}")
    
    print()


def example_7_backend_info():
    """Example 7: Check which backend is being used"""
    print("=" * 60)
    print("Example 7: Backend Information")
    print("=" * 60)
    
    backend = csh256.get_backend()
    print(f"Current backend: {backend}")
    
    if backend == 'C':
        print("✓ Using high-performance C extension")
    else:
        print("⚠ Using pure Python implementation (slower)")
        print("  Install C compiler and reinstall for better performance")
    
    print()


def example_8_salt_management():
    """Example 8: Manual salt management"""
    print("=" * 60)
    print("Example 8: Manual Salt Management")
    print("=" * 60)
    
    password = "my_password"
    
    # Generate a salt manually
    my_salt = csh256.generate_salt()
    print(f"Generated salt: {my_salt.hex()}")
    
    # Use the same salt multiple times (for testing/debugging only!)
    hash1 = csh256.hash(password, salt=my_salt, iterations=1000)
    hash2 = csh256.hash(password, salt=my_salt, iterations=1000)
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Hashes match: {hash1 == hash2}")
    print()
    print("Note: In production, always use auto-generated salts!")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("*" * 60)
    print("CSH-256 Usage Examples")
    print("*" * 60)
    print("\n")
    
    example_1_simple_hash()
    example_2_complete_hash()
    example_3_verify()
    example_4_custom_iterations()
    example_5_database_simulation()
    example_6_recommend_iterations()
    example_7_backend_info()
    example_8_salt_management()
    
    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)


if __name__ == '__main__':
    main()