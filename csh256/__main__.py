"""
Command-line interface for CSH-256
"""

import sys
import argparse
import getpass
from . import hash, hash_full, verify, generate_salt, recommend_iterations, get_backend
from ._version import __version__


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='csh256',
        description='CSH-256: Hybrid password hashing algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hash a password interactively
  csh256 hash

  # Hash with custom iterations
  csh256 hash -i 8192

  # Verify a password
  csh256 verify '$csh256$i=4096$...$...'

  # Recommend iterations for 500ms target
  csh256 recommend --target 500

  # Show backend info
  csh256 info
        """
    )
    
    parser.add_argument('--version', action='version', version=f'CSH-256 v{__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Hash command
    hash_parser = subparsers.add_parser('hash', help='Hash a password')
    hash_parser.add_argument('-p', '--password', help='Password to hash (will prompt if not provided)')
    hash_parser.add_argument('-i', '--iterations', type=int, default=4096,
                           help='Number of iterations (default: 4096)')
    hash_parser.add_argument('-s', '--salt', help='Salt in hex (auto-generated if not provided)')
    hash_parser.add_argument('-f', '--format', choices=['hex', 'phc'], default='phc',
                           help='Output format (default: phc)')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a password')
    verify_parser.add_argument('hash', help='PHC-formatted hash string')
    verify_parser.add_argument('-p', '--password', help='Password to verify (will prompt if not provided)')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Recommend iteration count')
    recommend_parser.add_argument('-t', '--target', type=float, default=250,
                                help='Target time in milliseconds (default: 250)')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run performance benchmark')
    benchmark_parser.add_argument('-i', '--iterations', type=int, nargs='+',
                                default=[1024, 2048, 4096, 8192],
                                help='Iteration counts to test')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show library information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'hash':
            return cmd_hash(args)
        elif args.command == 'verify':
            return cmd_verify(args)
        elif args.command == 'recommend':
            return cmd_recommend(args)
        elif args.command == 'benchmark':
            return cmd_benchmark(args)
        elif args.command == 'info':
            return cmd_info(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_hash(args):
    """Hash command implementation"""
    # Get password
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: Passwords do not match", file=sys.stderr)
            return 1
    
    # Get salt
    if args.salt:
        try:
            salt = bytes.fromhex(args.salt)
            if len(salt) != 16:
                print("Error: Salt must be exactly 16 bytes (32 hex characters)", file=sys.stderr)
                return 1
        except ValueError:
            print("Error: Invalid hex salt", file=sys.stderr)
            return 1
    else:
        salt = generate_salt()
    
    print(f"Hashing with {args.iterations} iterations...", file=sys.stderr)
    
    result = hash_full(password, salt=salt, iterations=args.iterations)
    
    if args.format == 'hex':
        print(f"Hash: {result['hash']}")
        print(f"Salt: {result['salt'].hex()}")
        print(f"Iterations: {result['iterations']}")
    else:  # phc
        print(result['formatted'])
    
    return 0


def cmd_verify(args):
    """Verify command implementation"""
    # Get password
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password: ")
    
    print("Verifying...", file=sys.stderr)
    
    is_valid = verify(password, formatted=args.hash)
    
    if is_valid:
        print("✓ Password is valid")
        return 0
    else:
        print("✗ Password is invalid")
        return 1


def cmd_recommend(args):
    """Recommend command implementation"""
    print(f"Benchmarking system performance (target: {args.target}ms)...", file=sys.stderr)
    
    iterations = recommend_iterations(args.target)
    
    print(f"\nRecommended iterations: {iterations}")
    print(f"This should take approximately {args.target}ms per hash")
    
    return 0


def cmd_benchmark(args):
    """Benchmark command implementation"""
    import time
    
    print(f"Backend: {get_backend()}")
    print(f"Running benchmarks...\n")
    
    test_password = b"benchmark_test_password_12345"
    test_salt = generate_salt()
    
    print(f"{'Iterations':<12} {'Time (s)':<12} {'Hashes/sec':<12}")
    print("-" * 40)
    
    for iterations in args.iterations:
        start = time.perf_counter()
        hash(test_password, salt=test_salt, iterations=iterations)
        elapsed = time.perf_counter() - start
        
        hashes_per_sec = 1.0 / elapsed if elapsed > 0 else 0
        
        print(f"{iterations:<12} {elapsed:<12.3f} {hashes_per_sec:<12.2f}")
    
    return 0


def cmd_info(args):
    """Info command implementation"""
    print(f"CSH-256 Library Information")
    print(f"=" * 40)
    print(f"Version: {__version__}")
    print(f"Backend: {get_backend()}")
    print(f"")
    print(f"Algorithm Specifications:")
    print(f"  Block Size: 512 bits")
    print(f"  Output Size: 256 bits")
    print(f"  Rounds per block: 64")
    print(f"  Default iterations: 4096")
    print(f"  Salt size: 16 bytes")
    print(f"")
    print(f"Security Features:")
    print(f"  ✓ AES S-Box non-linearity")
    print(f"  ✓ RSA-inspired modular exponentiation")
    print(f"  ✓ Configurable time-cost")
    print(f"  ✓ 51.56% avalanche effect")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())