'''
References:
- https://peteroupc.github.io/jump.pdf
- https://github.com/Lincoln-LM/RNG-Python-Scripts/blob/main/rng_related/jump_ahead.ipynb
- https://gist.github.com/oupo/d141f0809f824d8d6b48f8a2bee09514
'''

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..\..")

import numpy as np
import galois

from functools import reduce
from sympy import Matrix
from Util.Bits import bits_to_int

GF = galois.GF(2)

def int_to_gf2(x, size=32):
    bits = [(x >> i) & 1 for i in range(size)]
    return GF(np.array(bits, np.uint8))

def ints_to_gf2(xs, size=32):
    bits = [(xs[i // size] >> (i % size)) & 1 for i in range(size * len(xs))]
    return GF(np.array(bits, np.uint8))

def matrix_identity(size=32):
    return GF(np.identity(size, np.uint8))

def matrix_zero(size=32):
    return GF(np.zeros((size, size), np.uint8))

def matrix_constant(x, size=32):
    m = matrix_zero(size)
    np.fill_diagonal(m, int_to_gf2(x, size))
    return m

def matrix_lshift(n, size=32):
    return GF(np.eye(size, k=n, dtype=np.uint8).T)

def matrix_rshift(n, size=32):
    return matrix_lshift(-n, size)

def matrix_rotl(n, size=32):
    m = matrix_identity(size)
    return GF(np.roll(m, -n, axis=0).T)

def matrix_rotr(n, size=32):
    return matrix_rotl(-n, size)

def matrix_get_bit(b, size=32):
    m = matrix_zero(size)
    m[:, b] = 1
    return m 

def matrix_remove_bit(b, size=32):
    m = GF(np.zeros((size-1, size), np.uint8))
    for i in range(b):
        m[i, i] = 1
    for i in range(b, size-1):
        m[i, i+1] = 1
    return m

def matrix_add_bit(b, size=32):
    m = GF(np.zeros((size, size-1), np.uint8))
    for i in range(b):
        m[i, i] = 1
    for i in range(b, size-1):
        m[i+1, i] = 1
    return m

def matrix_inverse(mat):
    return np.linalg.inv(mat)

def matrix_power(mat, n):
    return np.linalg.matrix_power(mat, n)

def matrix_characteristic_polynomial(mat):
    charpoly = Matrix(mat).charpoly().all_coeffs() 
    return reduce(lambda p, q: (p << 1) | (q & 1), charpoly)

def gf2_mul_mod(a, b, m, degre):
    res = 0

    while a:
        if a & 1:
            res ^= b
        
        a >>= 1
        b <<= 1
        
        if b >> degre:
            b ^= m
    
    return res

def gf2_pow_mod(base, exp, mod, degre=128):
    res = 1

    while exp:
        if exp & 1:
            res = gf2_mul_mod(res, base, mod, degre)
        
        base = gf2_mul_mod(base, base, mod, degre)
        exp >>= 1
    
    return res

def print_matrix_table(mat, n=128, a=4):
    c = 1
    for i in range(n):
        x = bits_to_int(mat[i].tolist())
        print(f"0x{x:032X}", end=", ")
        if c % a == 0:
            print()
        c += 1

def print_jump_poly_table(charpoly, n, a=4, degre=128):
    c = 1
    for i in range(n):
        x = gf2_pow_mod(2, 1 << i, charpoly, degre)
        print(f"0x{x:032X}", end=", ")
        if c % a == 0:
            print()
        c += 1


##############################################################################################


def matrix_tinymt():
    state = matrix_identity(128)
    s0, s1, s2, s3 = (state[i:i+32] for i in range(0, 128, 32))

    x = matrix_constant(0x7fffffff) @ s0 ^ s1 ^ s2
    y = s3.copy()

    x ^= matrix_lshift(1) @ x
    y ^= matrix_rshift(1) @ y ^ x

    b = matrix_get_bit(0) @ y

    state[0:32] = s1
    state[32:64] = s2 ^ matrix_constant(0x8f7011ee) @ b
    state[64:96] = x ^ matrix_lshift(10) @ y ^ matrix_constant(0xfc78ff1f) @ b
    state[96:128] = y

    return state

# TinyMT output function is not F2-linear but at least with this we can compute the right lsb.
def matrix_tinymt_temper():
    state = matrix_identity(128)
    s0, s1, s2, s3 = (state[i:i+32] for i in range(0, 128, 32))

    t = s0 ^ matrix_rshift(8) @ s2
    return s3 ^ t ^ matrix_constant(0x3793fdff) @ matrix_get_bit(0) @ t 
   
def matrix_tinymt_127_lsb():
    state = matrix_identity(127)
    temper = matrix_tinymt_temper() @ matrix_add_bit(31, 128)
    next_state = matrix_remove_bit(31, 128) @ matrix_tinymt() @ matrix_add_bit(31, 128)

    m = matrix_zero(127)
    for i in range(127):
        t = temper @ state
        m[i] = t[0]
        state = next_state @ state
    
    return m

def matrix_xoroshiro():
    state = matrix_identity(128)
    s0 = state[64:128]
    s1 = state[0:64] ^ s0

    state[64:128] = matrix_rotl(24, 64) @ s0 ^ s1 ^ matrix_lshift(16, 64) @ s1
    state[0:64] = matrix_rotl(37, 64) @ s1
    
    return state

def matrix_xoroshiro_128_lsb():
    state = matrix_identity(128)
    next_state = matrix_xoroshiro()

    m = matrix_zero(128)
    for i in range(128):
        m[i] = state[0] ^ state[64]
        state = next_state @ state

    return m

def matrix_xorshift():
    state = matrix_identity(128)
    s3, s2, s1, s0 = (state[i:i+32] for i in range(0, 128, 32))

    t = s0.copy()
    t ^= matrix_lshift(11) @ t
    t ^= matrix_rshift(8) @ t
    t ^= s3 ^ matrix_rshift(19) @ s3

    state[96:128] = s1
    state[64:96] = s2
    state[32:64] = s3
    state[0:32] = t

    return state

if __name__ == "__main__":    
    '''mat = matrix_xoroshiro()
    charpoly = matrix_characteristic_polynomial(mat) # 0x10008828e513b43d5095b8f76579aa001
    print(hex(charpoly))

    inv = matrix_inverse(mat)
    test = mat @ inv
    print(np.array_equal(test, matrix_identity(128)))'''

    '''mat = matrix_tinymt()
    charpoly = matrix_characteristic_polynomial(mat) # 0x1b0a48045db1bfe951b98a18f31f57486
    print(hex(charpoly))'''

    '''mat = matrix_xorshift()
    charpoly = matrix_characteristic_polynomial(mat) # 0x1000000010046d8b3f985d65ffd3c8001
    print(hex(charpoly))'''

    '''inv = matrix_inverse(matrix_xoroshiro_128_lsb())
    print_matrix_table(inv)'''

    '''inv = matrix_inverse(matrix_tinymt_127_lsb())
    print_matrix_table(inv, 127)'''

    #print_jump_poly_table(0x1b0a48045db1bfe951b98a18f31f57486, 127)

    #print_jump_poly_table(0x10008828e513b43d5095b8f76579aa001, 128)

    print_jump_poly_table(0x1000000010046d8b3f985d65ffd3c8001, 128)