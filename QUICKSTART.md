# CSH-256 Quick Start Guide

## Installation

```bash
pip install csh256
```

## Basic Usage (30 seconds)

### 1. Hash a Password

```python
import csh256

# Simple hash (auto-generates salt)
hash_value = csh256.hash("my_password")
print(hash_value)
```

### 2. Get Complete Hash Info

```python
# Get hash with all components
result = csh256.hash_full("my_password")

print(f"Hash: {result['hash']}")
print(f"Salt: {result['salt'].hex()}")
print(f"Iterations: {result['iterations']}")
print(f"Store this: {result['formatted']}")
```

### 3. Verify a Password

```python
# Store the formatted hash
stored = result['formatted']

# Later, verify password
is_valid = csh256.verify("my_password", formatted=stored)
print(f"Valid: {is_valid}")  # True

is_valid = csh256.verify("wrong_password", formatted=stored)
print(f"Valid: {is_valid}")  # False
```

## Real-World Example (Database)

```python
import csh256

# Simulated database
users_db = {}

# User Registration
def register_user(username, password):
    result = csh256.hash_full(password)
    users_db[username] = result['formatted']
    print(f"✓ User {username} registered")

# User Login
def login_user(username, password):
    if username not in users_db:
        return False
    
    stored_hash = users_db[username]
    is_valid = csh256.verify(password, formatted=stored_hash)
    
    if is_valid:
        print(f"✓ Login successful")
    else:
        print(f"✗ Invalid password")
    
    return is_valid

# Usage
register_user("alice", "alice123")
login_user("alice", "alice123")     # Success
login_user("alice", "wrong")        # Fail
```

## Custom Security Level

```python
# Standard security (default 4096 iterations)
standard = csh256.hash_full("password", iterations=4096)

# High security (8192 iterations, ~2x slower)
high_security = csh256.hash_full("password", iterations=8192)

# Ultra security (16384 iterations, ~4x slower)
ultra = csh256.hash_full("password", iterations=16384)
```

## Command Line Usage

```bash
# Hash a password
csh256 hash

# Hash with custom iterations
csh256 hash -i 8192

# Verify a password
csh256 verify '$csh256$i=4096$...$...'

# Find optimal iterations for your system
csh256 recommend --target 500

# Show library info
csh256 info
```

## Performance Tuning

```python
# Find optimal iterations for 500ms computation time
recommended = csh256.recommend_iterations(500)
print(f"Use {recommended} iterations")

# Use the recommended value
result = csh256.hash_full("password", iterations=recommended)
```

## Flask Integration Example

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
    
    result = csh256.hash_full(password)
    users[username] = result['formatted']
    
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    if username not in users:
        return jsonify({'success': False})
    
    is_valid = csh256.verify(password, formatted=users[username])
    return jsonify({'success': is_valid})

if __name__ == '__main__':
    app.run()
```

## SQLite Integration Example

```python
import sqlite3
import csh256

# Create database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password_hash TEXT)''')

# Register user
def register(username, password):
    result = csh256.hash_full(password)
    c.execute("INSERT INTO users VALUES (?, ?)", 
              (username, result['formatted']))
    conn.commit()

# Verify user
def login(username, password):
    c.execute("SELECT password_hash FROM users WHERE username=?", 
              (username,))
    row = c.fetchone()
    
    if row is None:
        return False
    
    return csh256.verify(password, formatted=row[0])

# Usage
register("bob", "bob_password")
print(login("bob", "bob_password"))  # True
print(login("bob", "wrong"))         # False
```

## Security Best Practices

1. **Never store plain passwords** - Always hash them
2. **Use auto-generated salts** - Don't provide custom salts unless needed
3. **Adjust iterations** - Use `recommend_iterations()` to find optimal value
4. **Store formatted hash** - Use `result['formatted']` for storage
5. **Don't log passwords** - Be careful with debugging output

## Common Patterns

### Pattern 1: Simple API
```python
hash_value = csh256.hash("password")  # Just get the hash
```

### Pattern 2: Full Control
```python
result = csh256.hash_full("password", iterations=8192)
db.save(username, result['formatted'])
```

### Pattern 3: Verification
```python
stored = db.get_hash(username)
is_valid = csh256.verify(password, formatted=stored)
```

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