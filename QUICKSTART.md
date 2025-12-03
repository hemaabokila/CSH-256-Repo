# CSH-256 Complete API Documentation

## Table of Contents
1. [Core Functions](#core-functions)
2. [Utility Functions](#utility-functions)
3. [Helper Functions](#helper-functions)
4. [Examples](#examples)

---

## Core Functions

### `hash(password, salt=None, iterations=None)`

The simplest function to hash a password.

**Parameters:**
- `password` (str | bytes): The password to be encrypted
- `salt` (bytes, optional): 16-byte salt. If not specified, it's generated automatically
- `iterations` (int, optional): Number of iterations. Default: 4096

**Returns:**
- `str`: Hash in hexadecimal format (64 characters)

**Raises:**
- `ValueError`: If salt is not 16 bytes or iterations is less than 64

**Example:**
```python
import csh256

# Simple usage (generates salt automatically)
hash_value = csh256.hash("my_password")
print(hash_value)  # 'a3f2b1c4d5e6...'

# With custom salt
custom_salt = csh256.generate_salt()
hash_value = csh256.hash("my_password", salt=custom_salt)

# With custom iterations
hash_value = csh256.hash("my_password", iterations=8192)
```

**Note:** If you need to save the hash for later verification, use `hash_full()` instead of this function.

---

### `hash_full(password, salt=None, iterations=None)`

Generate a complete hash with all parameters. This is the recommended function for use in applications.

**Parameters:**
- `password` (str | bytes): The password to be encrypted
- `salt` (bytes, optional): 16-byte salt. If not specified, it's generated automatically
- `iterations` (int, optional): Number of iterations. Default: 4096

**Returns:**
- `dict`: Dictionary containing:
  - `'hash'` (str): The hash in hex format (64 characters)
  - `'salt'` (bytes): The salt used (16 bytes)
  - `'iterations'` (int): The number of iterations used
  - `'formatted'` (str): PHC-formatted text ready to save in database

**Raises:**
- `ValueError`: If salt is not 16 bytes or iterations is less than 64

**Example:**
```python
import csh256

# Generate complete hash
result = csh256.hash_full("my_password")

print(f"Hash: {result['hash']}")
print(f"Salt: {result['salt'].hex()}")
print(f"Iterations: {result['iterations']}")

# Save this in database
db.save(username, result['formatted'])

# With high security
result = csh256.hash_full("my_password", iterations=16384)
```

---

### `verify(password, hash_value=None, salt=None, iterations=None, formatted=None)`

Verify a password against a stored hash.

**Parameters:**
- `password` (str | bytes): The password to verify
- `hash_value` (str, optional): The stored hash (64 characters hex)
- `salt` (bytes, optional): The stored salt (16 bytes)
- `iterations` (int, optional): The stored iteration count
- `formatted` (str, optional): Alternative: PHC text containing all components

**Returns:**
- `bool`: `True` if password is correct, `False` if wrong

**Raises:**
- `ValueError`: If required components are not provided or if formatted string is invalid

**Example:**
```python
import csh256

# First method: using individual components
is_valid = csh256.verify("password", hash_value, salt, iterations)

# Second method: using formatted string (easier)
stored = "$csh256$i=4096$3f4e2a1b...$a3f2b1c4..."
is_valid = csh256.verify("password", formatted=stored)

# Practical example
def login(username, password):
    stored_hash = db.get_hash(username)
    return csh256.verify(password, formatted=stored_hash)
```

**Security Note:** This function uses `secrets.compare_digest()` for secure comparison against timing attacks.

---

### `format_hash(hash_value, salt, iterations)`

Format hash components into PHC string format.

**Parameters:**
- `hash_value` (str): Hash in hexadecimal format (64 characters)
- `salt` (bytes): The salt (16 bytes)
- `iterations` (int): Number of iterations

**Returns:**
- `str`: PHC-formatted text

**Format:**
```
$csh256$i=<iterations>$<salt_hex>$<hash>
```

**Example:**
```python
import csh256

hash_val = "a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2"
salt = bytes.fromhex("3f4e2a1b5c6d7e8f")
iterations = 4096

formatted = csh256.format_hash(hash_val, salt, iterations)
print(formatted)
# '$csh256$i=4096$3f4e2a1b5c6d7e8f$a3f2b1c4...'
```

---

### `parse_hash(formatted)`

Parse PHC string into its components.

**Parameters:**
- `formatted` (str): PHC-formatted text

**Returns:**
- `dict`: Dictionary containing:
  - `'hash'` (str): The hash
  - `'salt'` (bytes): The salt
  - `'iterations'` (int): Number of iterations

**Raises:**
- `ValueError`: If format is invalid

**Example:**
```python
import csh256

formatted = "$csh256$i=4096$3f4e2a1b5c6d7e8f$a3f2b1c4..."
components = csh256.parse_hash(formatted)

print(components['iterations'])  # 4096
print(components['salt'].hex())  # '3f4e2a1b5c6d7e8f'
print(components['hash'])        # 'a3f2b1c4...'
```

---

### `get_backend()`

Know which backend type is being used (C or Python).

**Returns:**
- `str`: `'C'` if using C extension, `'Python'` if using Pure Python

**Example:**
```python
import csh256

backend = csh256.get_backend()
print(f"Using {backend} backend")

# C extension is much faster than Pure Python
if backend == 'Python':
    print("Warning: Performance will be slower")
    print("Consider reinstalling with a C compiler")
```

---

## Utility Functions

### `generate_salt(size=16)`

Generate a secure random salt using `secrets`.

**Parameters:**
- `size` (int, optional): Salt size in bytes. Default: 16

**Returns:**
- `bytes`: Random bytes suitable for use as salt

**Example:**
```python
from csh256 import generate_salt

# Salt with default size
salt = generate_salt()
print(len(salt))  # 16

# Salt with custom size
salt = generate_salt(32)
print(len(salt))  # 32
```

**Security Note:** Uses `secrets.token_bytes()` which is safe for cryptographic use.

---

### `format_phc_string(hash_value, salt, iterations)`

Format components into PHC string (same as `format_hash`).

**Parameters:**
- `hash_value` (str): Hexadecimal hash
- `salt` (bytes): Salt bytes
- `iterations` (int): Number of iterations

**Returns:**
- `str`: PHC-formatted string

**Format:**
```
$csh256$i=<iterations>$<salt_hex>$<hash>
```

**Example:**
```python
from csh256.utils import format_phc_string

formatted = format_phc_string("a3f2...", b"salt...", 4096)
print(formatted)  # '$csh256$i=4096$73616c74...$a3f2...'
```

---

### `parse_phc_string(formatted)`

Parse PHC string into its components (same as `parse_hash`).

**Parameters:**
- `formatted` (str): PHC-formatted string

**Returns:**
- `dict`: Hash components

**Raises:**
- `ValueError`: If format is invalid

**Example:**
```python
from csh256.utils import parse_phc_string

formatted = "$csh256$i=4096$73616c74...$a3f2..."
components = parse_phc_string(formatted)
print(components['iterations'])  # 4096
```

---

### `recommend_iterations(target_time_ms=250)`

Recommend iteration count based on target time.

**Parameters:**
- `target_time_ms` (float, optional): Target time in milliseconds. Default: 250ms

**Returns:**
- `int`: Recommended iteration count

**Example:**
```python
from csh256.utils import recommend_iterations

# To get ~500ms computation time
recommended = recommend_iterations(500)
print(f"Use {recommended} iterations")

# Use the recommended value
result = csh256.hash_full("password", iterations=recommended)
```

**Note:** Performs a small benchmark on your system and calculates the appropriate count.

---

### `estimate_hash_time(iterations, sample_iterations=100)`

Estimate the time needed to compute a hash with a given iteration count.

**Parameters:**
- `iterations` (int): Target iteration count
- `sample_iterations` (int, optional): Number of iterations for testing. Default: 100

**Returns:**
- `float`: Estimated time in seconds

**Example:**
```python
from csh256.utils import estimate_hash_time

# Estimate time for 8192 iterations
time_sec = estimate_hash_time(8192)
print(f"Estimated time: {time_sec * 1000:.1f}ms")
```

**Note:** This is an approximate estimate. Actual time may vary based on system load.

---

### `validate_password_strength(password, min_length=8)`

Check password strength (helper function for applications).

**Parameters:**
- `password` (str): The password to check
- `min_length` (int, optional): Minimum length. Default: 8

**Returns:**
- `dict`: Dictionary containing:
  - `'valid'` (bool): `True` if password meets requirements
  - `'message'` (str): Description of validation result
  - `'score'` (int): Strength score (0-5)

**Checks:**
- Length (minimum 8)
- Lowercase letters
- Uppercase letters
- Digits
- Special characters

**Example:**
```python
from csh256.utils import validate_password_strength

# Strong password
result = validate_password_strength("MyP@ssw0rd")
print(result['valid'])    # True
print(result['score'])    # 5
print(result['message'])  # "Strong password"

# Weak password
result = validate_password_strength("weak")
print(result['valid'])    # False
print(result['score'])    # 1
print(result['message'])  # "Weak password: must be at least 8 characters, ..."
```

---

### `constant_time_compare(a, b)`

Compare two strings in constant time (protection against timing attacks).

**Parameters:**
- `a` (str): First string
- `b` (str): Second string

**Returns:**
- `bool`: `True` if equal, `False` if different

**Example:**
```python
from csh256.utils import constant_time_compare

is_equal = constant_time_compare("hash1", "hash2")
```

**Security Note:** Uses `secrets.compare_digest()` to ensure comparison takes the same time regardless of where the difference is.

---

### `hex_to_bytes(hex_string)` & `bytes_to_hex(data)`

Convert between hex strings and bytes.

**Parameters:**
- `hex_string` (str): Hexadecimal text
- `data` (bytes): Bytes data

**Returns:**
- `bytes` or `str`: Converted data

**Example:**
```python
from csh256.utils import hex_to_bytes, bytes_to_hex

# Hex to Bytes
salt = hex_to_bytes("3f4e2a1b5c6d7e8f")

# Bytes to Hex
hex_str = bytes_to_hex(salt)
print(hex_str)  # '3f4e2a1b5c6d7e8f'
```

---

## Helper Functions

### `get_default_iterations()`

Get the default iteration count.

**Returns:**
- `int`: Default iteration count (4096)

**Example:**
```python
import csh256

default = csh256.get_default_iterations()
print(default)  # 4096
```

---

### `set_default_iterations(iterations)`

Set the default iteration count for the future.

**Parameters:**
- `iterations` (int): New iteration count (must be >= 64)

**Raises:**
- `ValueError`: If iterations is less than 64

**Example:**
```python
import csh256

# Increase security
csh256.set_default_iterations(8192)

# Now every hash() will use 8192 iterations
hash_val = csh256.hash("password")
```

---

## Examples

### Example 1: Simple Login System

```python
import csh256

# Mock database
users_db = {}

def register(username, password):
    """Register a new user"""
    # Check password strength
    strength = csh256.utils.validate_password_strength(password)
    if not strength['valid']:
        return {'success': False, 'error': strength['message']}
    
    # Hash the password
    result = csh256.hash_full(password)
    users_db[username] = result['formatted']
    
    return {'success': True, 'message': f"User {username} registered"}

def login(username, password):
    """User login"""
    if username not in users_db:
        return {'success': False, 'error': "User not found"}
    
    stored_hash = users_db[username]
    is_valid = csh256.verify(password, formatted=stored_hash)
    
    if is_valid:
        return {'success': True, 'message': "Login successful"}
    else:
        return {'success': False, 'error': "Invalid password"}

# Usage
print(register("alice", "Alice@123"))
print(login("alice", "Alice@123"))
print(login("alice", "wrong"))
```

---

### Example 2: Flask Integration

```python
from flask import Flask, request, jsonify
import csh256

app = Flask(__name__)
users = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    # Check strength
    strength = csh256.utils.validate_password_strength(password)
    if not strength['valid']:
        return jsonify({'success': False, 'error': strength['message']}), 400
    
    # Hash and save
    result = csh256.hash_full(password)
    users[username] = result['formatted']
    
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    if username not in users:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    is_valid = csh256.verify(password, formatted=users[username])
    
    if is_valid:
        return jsonify({'success': True, 'token': 'your_jwt_token'})
    else:
        return jsonify({'success': False, 'error': 'Invalid password'}), 401

if __name__ == '__main__':
    app.run()
```

---

### Example 3: SQLite Integration

```python
import sqlite3
import csh256

class UserDB:
    def __init__(self, db_path='users.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def register(self, username, password):
        """Register a new user"""
        # Check strength
        strength = csh256.utils.validate_password_strength(password)
        if not strength['valid']:
            raise ValueError(strength['message'])
        
        # Hash
        result = csh256.hash_full(password)
        
        # Save in database
        try:
            self.conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, result['formatted'])
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")
    
    def login(self, username, password):
        """User login"""
        cursor = self.conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return False
        
        return csh256.verify(password, formatted=row[0])
    
    def close(self):
        self.conn.close()

# Usage
db = UserDB()
db.register("bob", "Bob@Pass123")
print(db.login("bob", "Bob@Pass123"))  # True
print(db.login("bob", "wrong"))        # False
db.close()
```

---

### Example 4: Performance Tuning

```python
import csh256
from csh256.utils import recommend_iterations, estimate_hash_time

# Find the best iteration count for your system
print("Finding optimal iterations...")

# To get ~500ms computation time
recommended = recommend_iterations(target_time_ms=500)
print(f"Recommended iterations: {recommended}")

# Estimate time
time_sec = estimate_hash_time(recommended)
print(f"Estimated time: {time_sec * 1000:.1f}ms")

# Use the recommended value
csh256.set_default_iterations(recommended)

# Now every hash will use the new value
result = csh256.hash_full("password")
print(f"Using {result['iterations']} iterations")
```

---

### Example 5: Different Security Levels

```python
import csh256

class SecurityLevels:
    STANDARD = 4096    # ~250ms - for normal use
    HIGH = 8192        # ~500ms - for important accounts
    ULTRA = 16384      # ~1000ms - for very sensitive data
    MAXIMUM = 32768    # ~2000ms - for maximum security

def hash_with_level(password, level):
    """Hash with specified security level"""
    return csh256.hash_full(password, iterations=level)

# Use different levels
user_password = hash_with_level("user123", SecurityLevels.STANDARD)
admin_password = hash_with_level("admin123", SecurityLevels.HIGH)
root_password = hash_with_level("root123", SecurityLevels.ULTRA)

print(f"User iterations: {user_password['iterations']}")
print(f"Admin iterations: {admin_password['iterations']}")
print(f"Root iterations: {root_password['iterations']}")
```

---

## Constants

```python
DEFAULT_ITERATIONS = 4096    # Default iteration count
DEFAULT_SALT_SIZE = 16       # Salt size in bytes
MIN_ITERATIONS = 64          # Minimum iterations
```

---

## Security Best Practices

### ✅ Do's:
1. **Use `hash_full()`** to get all components
2. **Save `formatted` string** in database
3. **Use `generate_salt()`** to generate random salt
4. **Adjust iterations** according to your system using `recommend_iterations()`
5. **Check password strength** before registration

### ❌ Don'ts:
1. **Never save passwords without hashing**
2. **Don't use fixed salt** for all users
3. **Don't reduce iterations** below minimum (64)
4. **Don't log passwords** in logs
5. **Don't share formatted strings** between different systems

---

## PHC String Format

Standard format for saving hash:

```
$csh256$i=<iterations>$<salt_hex>$<hash>
```

**Example:**
```
$csh256$i=4096$3f4e2a1b5c6d7e8f9a0b1c2d3e4f5a6b$a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2
```

**Components:**
- `$csh256$` - Identifier
- `i=4096` - Iteration count
- `3f4e2a1b...` - Salt (hex)
- `a3f2b1c4...` - Hash (hex)

---

## Error Handling

```python
import csh256

try:
    result = csh256.hash_full("password", iterations=32)
except ValueError as e:
    print(f"Error: {e}")
    # "Iterations must be at least 64"

try:
    is_valid = csh256.verify("password", formatted="invalid")
except ValueError as e:
    print(f"Error: {e}")
    # "Invalid formatted hash string: ..."
```

---

## Version Information

```python
import csh256

print(csh256.__version__)  # Example: '1.0.0'
```

---



## Troubleshooting

### Slow Performance?

Check if C extension is being used:
```python
print(csh256.get_backend())  # Should show 'C'
```

If showing 'Python', reinstall with compiler:
```bash
pip uninstall csh256
pip install csh256 --force-reinstall
```

### ImportError?

Install without C extension:
```bash
pip install csh256 --no-binary csh256
```

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [examples/](examples/) for more code samples
- See [BUILD_AND_PUBLISH.md](BUILD_AND_PUBLISH.md) for development setup

## Support

- GitHub: https://github.com/hemaabokila/CSH-256-Repo
- Issues: https://github.com/hemaabokila/CSH-256-Repo/issues
- PyPI: https://pypi.org/project/csh256/

## License

MIT License - Ibrahim Hilal Aboukila