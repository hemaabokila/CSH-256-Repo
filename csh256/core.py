"""
Pure Python implementation of CSH-256
This is a fallback when C extension is not available
"""

import struct
from typing import List


# === CONSTANTS ===

HVs = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
]

K_t = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]

SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

MODULUS_N = 0xFFFFFFFFFFFFFFFF
MASK_32 = 0xFFFFFFFF


# === UTILITY FUNCTIONS ===

def _rotr(x: int, n: int, width: int = 32) -> int:
    """32-bit Rotate Right"""
    return ((x >> n) | (x << (width - n))) & MASK_32


def _shr(x: int, n: int) -> int:
    """32-bit Shift Right"""
    return (x >> n) & MASK_32


def _add32(*args: int) -> int:
    """Add multiple 32-bit words, modulo 2^32"""
    return sum(args) & MASK_32


def _bytes_to_words(data: bytes) -> List[int]:
    """Convert byte block to 32-bit words (big-endian)"""
    return list(struct.unpack('>16I', data))


def _words_to_bytes(words: List[int]) -> bytes:
    """Convert 32-bit words to bytes (big-endian)"""
    return struct.pack('>8I', *words)


# === SHA-256 LOGICAL FUNCTIONS ===

def sigma0(x: int) -> int:
    """σ0(X) = ROTR^7(X) ⊕ ROTR^18(X) ⊕ SHR^3(X)"""
    return _rotr(x, 7) ^ _rotr(x, 18) ^ _shr(x, 3)


def sigma1(x: int) -> int:
    """σ1(X) = ROTR^17(X) ⊕ ROTR^19(X) ⊕ SHR^10(X)"""
    return _rotr(x, 17) ^ _rotr(x, 19) ^ _shr(x, 10)


def Sigma0(a: int) -> int:
    """Σ0(A) = ROTR^2(A) ⊕ ROTR^13(A) ⊕ ROTR^22(A)"""
    return _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)


def Sigma1(e: int) -> int:
    """Σ1(E) = ROTR^6(E) ⊕ ROTR^11(E) ⊕ ROTR^25(E)"""
    return _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)


def CH(e: int, f: int, g: int) -> int:
    """CH(E, F, G) = (E & F) ⊕ (~E & G)"""
    return (e & f) ^ (~e & g) & MASK_32


def MAJ(a: int, b: int, c: int) -> int:
    """MAJ(A, B, C) = (A & B) ⊕ (A & C) ⊕ (B & C)"""
    return (a & b) ^ (a & c) ^ (b & c)


# === CSH-256 CUSTOM FUNCTIONS ===

def _sbox_transform(word: int) -> int:
    """Apply AES S-Box to each byte of 32-bit word"""
    result = 0
    for i in range(4):
        byte_val = (word >> (8 * (3 - i))) & 0xFF
        sbox_val = SBOX[byte_val]
        result |= (sbox_val << (8 * (3 - i)))
    return result


def _padding(message_bytes: bytes) -> bytes:
    """Merkle-Damgård padding"""
    mlen = len(message_bytes) * 8
    
    padded_message = bytearray(message_bytes)
    padded_message.append(0x80)
    
    while (len(padded_message) * 8) % 512 != 448:
        padded_message.append(0x00)
    
    padded_message.extend(struct.pack('>Q', mlen))
    
    return bytes(padded_message)


def _compress(H: List[int], block: bytes, is_single_block_mode: bool = False) -> List[int]:
    """Compression function - 64 rounds"""
    # Message expansion
    W = _bytes_to_words(block)
    
    for t in range(16, 64):
        s1 = sigma1(W[t-2])
        s0 = sigma0(W[t-15])
        W_t = _add32(s1, W[t-7], s0, W[t-16])
        W.append(W_t)
    
    # Initialize working variables
    a, b, c, d, e, f, g, h = H[:]
    
    # 64 rounds
    for t in range(64):
        # Step 2: Non-Linear Layer (AES S-Box)
        a_sbox = _sbox_transform(a)
        e_sbox = _sbox_transform(e)
        
        # Step 1 & 4: Logical Mixing
        T1 = _add32(h, Sigma1(e_sbox), CH(e_sbox, f, g), K_t[t], W[t])
        T2 = _add32(Sigma0(a_sbox), MAJ(a_sbox, b, c))
        
        # Step 3: Computational Slowdown (RSA Primitive)
        H_Inj = 0
        if t % 8 == 7:
            h_cubed = pow(h, 3, MODULUS_N)
            H_Inj = h_cubed & MASK_32
        
        # State update
        h = g
        g = f
        f = e
        e = _add32(d, T1)
        d = c
        c = b
        b = a ^ H_Inj
        a = _add32(T1, T2)
    
    # Merkle-Damgård finalization
    H[0] = _add32(H[0], a)
    H[1] = _add32(H[1], b)
    H[2] = _add32(H[2], c)
    H[3] = _add32(H[3], d)
    H[4] = _add32(H[4], e)
    H[5] = _add32(H[5], f)
    H[6] = _add32(H[6], g)
    H[7] = _add32(H[7], h)
    
    return H


def hash(data: bytes, salt: bytes, iterations: int) -> str:
    """
    Main CSH-256 hashing function
    
    Args:
        data: Password/data to hash
        salt: 16-byte salt
        iterations: Number of iterations (min 64)
    
    Returns:
        64-character hexadecimal hash string
    """
    if iterations < 64:
        raise ValueError("Iterations must be minimum 64 for time-cost resistance.")
    
    if len(salt) != 16:
        raise ValueError("Salt must be exactly 16 bytes")
    
    # Initial Hash: H(0) = CSH-256-SinglePass(Data || Salt)
    message = data + salt
    padded_message = _padding(message)
    
    blocks = [padded_message[i:i+64] for i in range(0, len(padded_message), 64)]
    
    H_state = list(HVs)
    
    for block in blocks:
        H_state = _compress(H_state, block)
    
    H_i = H_state
    
    # Time-Cost Iteration
    ZERO_PADDING_32_BYTES = b'\x00' * 32
    
    for i in range(1, iterations):
        hash_bytes = _words_to_bytes(H_i)
        single_block = hash_bytes + ZERO_PADDING_32_BYTES
        
        H_temp = list(HVs)
        H_i = _compress(H_temp, single_block, is_single_block_mode=True)
    
    final_bytes = _words_to_bytes(H_i)
    return final_bytes.hex()