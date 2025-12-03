/*
 * CSH-256: Custom Secure Hash - 256 bit
 * High-performance C implementation
 * Author: Ibrahim Hilal Aboukila
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <string.h>

/* ==================== CONSTANTS ==================== */

#ifdef _MSC_VER
typedef uint64_t __uint128_t;
#else
typedef unsigned __int128 __uint128_t;
#endif

/* Initial Hash Values - First 8 primes sqrt(p) */
static const uint32_t HVs[8] = {
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};

/* Round Constants - First 64 primes cbrt(p) */
static const uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};

/* AES S-Box */
static const uint8_t SBOX[256] = {
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
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16};

/* ==================== UTILITY MACROS ==================== */

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define SHR(x, n) ((x) >> (n))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define SIGMA0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define SIGMA1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define sigma0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ SHR(x, 3))
#define sigma1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ SHR(x, 10))

/* ==================== HELPER FUNCTIONS ==================== */

/* Apply AES S-Box to each byte of a 32-bit word */
static inline uint32_t sbox_transform(uint32_t word)
{
    uint32_t result = 0;
    result |= (uint32_t)SBOX[(word >> 24) & 0xFF] << 24;
    result |= (uint32_t)SBOX[(word >> 16) & 0xFF] << 16;
    result |= (uint32_t)SBOX[(word >> 8) & 0xFF] << 8;
    result |= (uint32_t)SBOX[word & 0xFF];
    return result;
}

/* Modular exponentiation: (base^exp) mod modulus */
static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t modulus)
{
    uint64_t result = 1;
    base %= modulus;
    while (exp > 0)
    {
        if (exp & 1)
        {
            result = (__uint128_t)result * base % modulus;
        }
        base = (__uint128_t)base * base % modulus;
        exp >>= 1;
    }
    return result;
}

/* Convert bytes to big-endian 32-bit words */
static void bytes_to_words(const uint8_t *bytes, uint32_t *words, size_t count)
{
    for (size_t i = 0; i < count; i++)
    {
        words[i] = ((uint32_t)bytes[i * 4] << 24) |
                   ((uint32_t)bytes[i * 4 + 1] << 16) |
                   ((uint32_t)bytes[i * 4 + 2] << 8) |
                   ((uint32_t)bytes[i * 4 + 3]);
    }
}

/* Convert big-endian 32-bit words to bytes */
static void words_to_bytes(const uint32_t *words, uint8_t *bytes, size_t count)
{
    for (size_t i = 0; i < count; i++)
    {
        bytes[i * 4] = (words[i] >> 24) & 0xFF;
        bytes[i * 4 + 1] = (words[i] >> 16) & 0xFF;
        bytes[i * 4 + 2] = (words[i] >> 8) & 0xFF;
        bytes[i * 4 + 3] = words[i] & 0xFF;
    }
}

/* ==================== COMPRESSION FUNCTION ==================== */

static void compress(uint32_t H[8], const uint8_t block[64])
{
    uint32_t W[64];
    uint32_t a, b, c, d, e, f, g, h;
    uint32_t T1, T2;
    int t;

    /* Message expansion */
    bytes_to_words(block, W, 16);
    for (t = 16; t < 64; t++)
    {
        W[t] = sigma1(W[t - 2]) + W[t - 7] + sigma0(W[t - 15]) + W[t - 16];
    }

    /* Initialize working variables */
    a = H[0];
    b = H[1];
    c = H[2];
    d = H[3];
    e = H[4];
    f = H[5];
    g = H[6];
    h = H[7];

    /* 64 rounds */
    for (t = 0; t < 64; t++)
    {
        uint32_t H_Inj = 0;
        /* Step 2: Non-Linear Layer (AES S-Box) */
        uint32_t a_sbox = sbox_transform(a);
        uint32_t e_sbox = sbox_transform(e);

        /* Step 1 & 4: Logical Mixing */
        T1 = h + SIGMA1(e_sbox) + CH(e_sbox, f, g) + K[t] + W[t];
        T2 = SIGMA0(a_sbox) + MAJ(a_sbox, b, c);

        /* Step 3: Computational Slowdown (RSA Primitive) */
        if (t % 8 == 7)
        {
            uint64_t h_64 = (uint64_t)h;
            uint64_t h_cubed = mod_pow(h_64, 3, 0xFFFFFFFFFFFFFFFFULL);
            H_Inj = (uint32_t)(h_cubed & 0xFFFFFFFF);
        }

        /* State update */
        h = g;
        g = f;
        f = e;
        e = d + T1;
        d = c;
        c = b;
        b = a ^ H_Inj;
        a = T1 + T2;
    }

    /* Merkle-Damgård finalization */
    H[0] += a;
    H[1] += b;
    H[2] += c;
    H[3] += d;
    H[4] += e;
    H[5] += f;
    H[6] += g;
    H[7] += h;
}

/* ==================== PADDING FUNCTION ==================== */

static void pad_message(const uint8_t *msg, size_t msg_len, uint8_t **padded, size_t *padded_len)
{
    uint64_t bit_len = msg_len * 8;
    size_t pad_len = msg_len + 1;

    /* Calculate padding: must be 448 bits mod 512 */
    while ((pad_len * 8) % 512 != 448)
    {
        pad_len++;
    }
    pad_len += 8; /* Add 64-bit length */

    *padded = (uint8_t *)malloc(pad_len);
    if (!*padded)
        return;

    memcpy(*padded, msg, msg_len);
    (*padded)[msg_len] = 0x80;
    memset(*padded + msg_len + 1, 0, pad_len - msg_len - 9);

    /* Append length as big-endian 64-bit */
    for (int i = 0; i < 8; i++)
    {
        (*padded)[pad_len - 8 + i] = (bit_len >> (56 - i * 8)) & 0xFF;
    }

    *padded_len = pad_len;
}

/* ==================== MAIN CSH-256 FUNCTION ==================== */

static void csh256_hash(const uint8_t *data, size_t data_len,
                        const uint8_t *salt, size_t salt_len,
                        uint32_t iterations,
                        uint8_t output[32])
{
    uint32_t H[8];
    uint8_t *combined = NULL;
    uint8_t *padded = NULL;
    size_t combined_len, padded_len;

    /* Step 1: Initial Hash H(0) = CSH(Data || Salt) */
    combined_len = data_len + salt_len;
    combined = (uint8_t *)malloc(combined_len);
    if (!combined)
        return;

    memcpy(combined, data, data_len);
    memcpy(combined + data_len, salt, salt_len);

    pad_message(combined, combined_len, &padded, &padded_len);
    free(combined);
    if (!padded)
        return;

    /* Initialize H with HVs */
    memcpy(H, HVs, sizeof(HVs));

    /* Process all blocks */
    for (size_t i = 0; i < padded_len; i += 64)
    {
        compress(H, padded + i);
    }
    free(padded);

    /* Step 2: Time-Cost Iteration */
    uint8_t single_block[64];
    for (uint32_t iter = 1; iter < iterations; iter++)
    {
        /* H(i-1) to bytes + zero padding */
        words_to_bytes(H, single_block, 8);
        memset(single_block + 32, 0, 32);

        /* Reset H to HVs */
        memcpy(H, HVs, sizeof(HVs));

        /* Compress single block */
        compress(H, single_block);
    }

    /* Final output */
    words_to_bytes(H, output, 8);
}

/* ==================== PYTHON INTERFACE ==================== */

static PyObject *py_csh256(PyObject *self, PyObject *args, PyObject *kwargs)
{
    const char *data;
    const char *salt;
    Py_ssize_t data_len, salt_len;
    uint32_t iterations = 4096;
    uint8_t output[32];
    char hex_output[65];

    static char *kwlist[] = {"data", "salt", "iterations", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#s#|I", kwlist,
                                     &data, &data_len, &salt, &salt_len, &iterations))
    {
        return NULL;
    }

    if (salt_len != 16)
    {
        PyErr_SetString(PyExc_ValueError, "Salt must be exactly 16 bytes");
        return NULL;
    }

    if (iterations < 64)
    {
        PyErr_SetString(PyExc_ValueError, "Iterations must be at least 64");
        return NULL;
    }

    /* Allow Python threads during computation */
    Py_BEGIN_ALLOW_THREADS
        csh256_hash((uint8_t *)data, data_len, (uint8_t *)salt, salt_len, iterations, output);
    Py_END_ALLOW_THREADS

        /* Convert to hex */
        for (int i = 0; i < 32; i++)
    {
        sprintf(hex_output + i * 2, "%02x", output[i]);
    }
    hex_output[64] = '\0';

    return PyUnicode_FromString(hex_output);
}

/* Module methods */
static PyMethodDef CSH256Methods[] = {
    {"hash", (PyCFunction)py_csh256, METH_VARARGS | METH_KEYWORDS,
     "Compute CSH-256 hash"},
    {NULL, NULL, 0, NULL}};

/* Module definition */
static struct PyModuleDef csh256module = {
    PyModuleDef_HEAD_INIT,
    "_csh256",
    "CSH-256 C extension for high-performance password hashing",
    -1,
    CSH256Methods};

/* Module initialization */
PyMODINIT_FUNC PyInit__csh256(void)
{
    return PyModule_Create(&csh256module);
}