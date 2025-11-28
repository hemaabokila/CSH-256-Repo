# CSH-256 Build and Publishing Guide

## Project Structure

```
csh256/
├── setup.py                    # Main setup file
├── setup.cfg                   # Setup configuration
├── pyproject.toml             # Modern Python packaging
├── MANIFEST.in                # Files to include
├── README.md                   # Documentation
├── LICENSE                     # MIT License
├── BUILD_AND_PUBLISH.md       # This file
│
├── csh256/
│   ├── __init__.py            # Main API
│   ├── __main__.py            # CLI interface
│   ├── _version.py            # Version
│   ├── core.py                # Pure Python fallback
│   ├── utils.py               # Utilities
│   └── _csh256.c              # C extension
│
├── tests/
│   ├── __init__.py
│   ├── test_basic.py
│   ├── test_avalanche.py
│   └── test_performance.py
│
└── examples/
    ├── basic_usage.py
    ├── with_database.py
    └── password_verification.py
```

## Prerequisites

### System Requirements

1. **Python 3.8+**
```bash
python --version
```

2. **C Compiler** (for C extension)
   - **Linux**: GCC
     ```bash
     sudo apt-get install build-essential python3-dev
     ```
   - **macOS**: Xcode Command Line Tools
     ```bash
     xcode-select --install
     ```
   - **Windows**: Microsoft Visual C++ Build Tools
     - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

3. **Build Tools**
```bash
pip install --upgrade pip setuptools wheel
pip install build twine
```

## Development Setup

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 2. Verify Installation

```bash
# Check if installed correctly
python -c "import csh256; print(csh256.__version__)"

# Check backend (should be 'C' if compiled successfully)
python -c "import csh256; print(csh256.get_backend())"

# Run basic test
python -c "import csh256; print(csh256.hash('test'))"
```

## Testing

### Run All Tests

```bash
# Basic tests
pytest tests/ -v

# With coverage
pytest --cov=csh256 --cov-report=html tests/

# Run specific test file
pytest tests/test_basic.py -v

# Run benchmarks
pytest tests/test_performance.py -v
```

### Run Examples

```bash
python examples/basic_usage.py
```

### CLI Testing

```bash
# Show help
csh256 --help

# Hash a password
csh256 hash -p "test_password" -i 1000

# Verify
csh256 verify '$csh256$i=1000$...$...' -p "test_password"

# Recommend iterations
csh256 recommend --target 500

# Benchmark
csh256 benchmark -i 1024 2048 4096

# Show info
csh256 info
```

## Building for Distribution

### 1. Clean Previous Builds

```bash
# Remove old build files
rm -rf build/ dist/ *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.so" -delete
```

### 2. Build Source Distribution and Wheel

```bash
# Build both source and wheel distributions
python -m build

# This creates:
# - dist/csh256-1.0.0.tar.gz (source distribution)
# - dist/csh256-1.0.0-cp38-cp38-linux_x86_64.whl (wheel for current platform)
```

### 3. Test the Built Package

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# Install from the built wheel
pip install dist/csh256-1.0.0-*.whl

# Test it
python -c "import csh256; print(csh256.hash('test'))"
python -c "import csh256; print(csh256.get_backend())"

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

## Publishing to PyPI

### 1. Create PyPI Account

1. Register at https://pypi.org/account/register/
2. Verify your email
3. Enable 2FA (recommended)
4. Create API token:
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope "Entire account"
   - Save the token (starts with `pypi-`)

### 2. Configure Credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
repository = https://test.pypi.org/legacy/
```

Or use environment variable:
```bash
export TWINE_PASSWORD=pypi-YOUR-API-TOKEN-HERE
```

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ csh256

# Test the package
python -c "import csh256; print(csh256.hash('test'))"
```

### 4. Publish to PyPI

```bash
# Upload to real PyPI
python -m twine upload dist/*

# You'll be prompted for username and password
# Username: __token__
# Password: your-api-token
```

### 5. Verify Publication

```bash
# Check if package is live
pip install csh256

# Or visit: https://pypi.org/project/csh256/
```

## Version Management

### Updating Version

Edit `csh256/_version.py`:

```python
__version__ = "1.0.1"  # Increment version
```

Follow semantic versioning:
- **1.0.0** → **1.0.1**: Bug fixes (patch)
- **1.0.0** → **1.1.0**: New features, backward compatible (minor)
- **1.0.0** → **2.0.0**: Breaking changes (major)

### Release Checklist

- [ ] Update version in `_version.py`
- [ ] Update CHANGELOG.md (if exists)
- [ ] Run all tests: `pytest tests/`
- [ ] Update README.md if needed
- [ ] Clean build directories
- [ ] Build new distributions: `python -m build`
- [ ] Test installation locally
- [ ] Upload to TestPyPI
- [ ] Test from TestPyPI
- [ ] Upload to PyPI
- [ ] Create Git tag: `git tag v1.0.1`
- [ ] Push tag: `git push origin v1.0.1`

## Platform-Specific Wheels

### Building for Multiple Platforms

For better user experience, build wheels for different platforms:

#### Using cibuildwheel (Recommended)

```bash
# Install cibuildwheel
pip install cibuildwheel

# Build wheels for all platforms
cibuildwheel --platform linux
cibuildwheel --platform macos
cibuildwheel --platform windows
```

#### Manual Cross-Platform Builds

**Linux (using Docker):**
```bash
docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2014_x86_64 /io/build_wheels.sh
```

**macOS:**
```bash
python -m build
```

**Windows:**
```cmd
python -m build
```

## Troubleshooting

### C Extension Fails to Build

**Problem**: Compiler errors during installation

**Solutions**:
1. Install compiler (see Prerequisites)
2. Install as pure Python:
   ```bash
   pip install csh256 --no-binary csh256
   ```
3. Check error logs in build output

### ImportError: No module named '_csh256'

**Problem**: C extension not compiled

**Solution**: Reinstall with compilation:
```bash
pip uninstall csh256
pip install csh256 --force-reinstall
```

### Slow Performance

**Problem**: Using Python backend instead of C

**Check**:
```python
import csh256
print(csh256.get_backend())  # Should print 'C'
```

**Solution**: Ensure C extension compiled successfully

### PyPI Upload Fails

**Common Issues**:
1. **Version already exists**: Increment version number
2. **Authentication failed**: Check API token
3. **File already uploaded**: Clean and rebuild

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run tests
      run: pytest tests/ -v
    
    - name: Check backend
      run: python -c "import csh256; print(csh256.get_backend())"
```

## Best Practices

1. **Always test before publishing**
2. **Use TestPyPI first**
3. **Semantic versioning**
4. **Keep CHANGELOG updated**
5. **Tag releases in Git**
6. **Build wheels for common platforms**
7. **Include comprehensive tests**
8. **Document breaking changes**

## Support

For issues or questions:
- GitHub Issues: https://github.com/hemaabokila/CSH-256-Repo/issues
- Email: ibrahemabokila@gmail.com

## Additional Resources

- Python Packaging Guide: https://packaging.python.org/
- PyPI Help: https://pypi.org/help/
- Setuptools Documentation: https://setuptools.pypa.io/
- Building C Extensions: https://docs.python.org/3/extending/building.html