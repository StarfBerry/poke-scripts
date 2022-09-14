'''
References:
- https://peteroupc.github.io/jump.pdf
- https://github.com/Lincoln-LM/RNG-Python-Scripts/blob/main/rng_related/jump_ahead.md
'''

import numpy as np
import galois

from sympy import Matrix
from functools import reduce
from GF2 import gf2_to_int

GF = galois.GF(2)

def int_to_gf2(x, size=64):
    bits = [(x >> i) & 1 for i in range(size)]
    return GF(np.array(bits, np.uint8))

def ints_to_gf2(xs, size=64):
    bits = [(xs[i // size] >> (i % size)) & 1 for i in range(size * len(xs))]
    return GF(np.array(bits, np.uint8))

def matrix_identity(size=64):
    return GF(np.identity(size, np.uint8))

def matrix_zero(size=64):
    return GF(np.zeros((size, size), np.uint8))

def matrix_constant(x, size=64):
    m = matrix_zero(size)
    np.fill_diagonal(m, int_to_gf2(x, size))
    return m

def matrix_lshift(n, size=64):
    return GF(np.eye(size, k=n, dtype=np.uint8))

def matrix_rshift(n, size=64):
    return matrix_lshift(-n, size)

def matrix_rotr(n, size=64):
    rotr = matrix_identity(size)
    return GF(np.roll(rotr, n, axis=0))

def matrix_rotl(n, size=64):
    return matrix_rotr(-n, size)

def matrix_get_bit(b, size=64):
    m = matrix_zero(size)
    m[b, :] = 1
    return m 

def matrix_remove_bit(b, size=64):
    m = GF(np.zeros((size, size-1), np.uint8))
    for i in range(b):
        m[i, i] = 1
    for i in range(b, size-1):
        m[i+1, i] = 1
    return m

def matrix_add_bit(b, size=64):
    m = GF(np.zeros((size-1, size), np.uint8))
    for i in range(b):
        m[i, i] = 1
    for i in range(b, size-1):
        m[i, i+1] = 1
    return m

def matrix_inverse(mat):
    return np.linalg.inv(mat)

def matrix_power(mat, n):
    return np.linalg.matrix_power(mat, n)

def matrix_characteristic_polynomial(mat):
    charpoly = Matrix(mat).charpoly().all_coeffs() 
    return reduce(lambda p, q: (p << 1) | (q & 1), charpoly)


##############################################################################################


'''
# If you want your pc to die

def matrix_mersenne_twister():
    size = 32 * 624
    state = matrix_identity(size)

    for i in range(0, size, 32):
        a = (i + 32) % size
        b = (i + 32 * 397) % size

        x = state[:, i:i+32] @ matrix_constant(0x80000000, 32) | state[:, a:a+32] @ matrix_constant(0x7fffffff, 32)
        y = x @ matrix_rshift(1, 32) ^ x @ matrix_get_bit(0, 32) @ matrix_constant(0x9908b0df, 32)

        state[:, i:i+32] = state[:, b:b+32] ^ y
    
    return state
'''

def matrix_tinymt():
    state = matrix_identity(128)
    s0, s1, s2, s3 = (state[:, i:i+32] for i in range(0, 128, 32))

    x = s0 @ matrix_constant(0x7fffffff, 32) ^ s1 ^ s2
    y = s3.copy()

    x ^= x @ matrix_lshift(1, 32)
    y ^= y @ matrix_rshift(1, 32) ^ x

    b = y @ matrix_get_bit(0, 32)

    state[:, 0:32] = s1
    state[:, 32:64] = s2 ^ b @ matrix_constant(0x8f7011ee, 32)
    state[:, 64:96] = x ^ y @ matrix_lshift(10, 32) ^ b @ matrix_constant(0xfc78ff1f, 32)
    state[:, 96:128] = y

    return state

# TinyMT output function is not F2-linear but at least with this we can compute the right lsb.
def matrix_tinymt_temper():
    state = matrix_identity(128)
    s0, s1, s2, s3 = (state[:, i:i+32] for i in range(0, 128, 32))

    t = s0 ^ s2 @ matrix_rshift(8, 32)
    return s3 ^ t ^ t @ matrix_get_bit(0, 32) @ matrix_constant(0x3793fdff, 32)
   
def matrix_tinymt_127_lsb():
    state = matrix_identity(127)
    temper = matrix_add_bit(31, 128) @ matrix_tinymt_temper()
    next_state = matrix_add_bit(31, 128) @ matrix_tinymt() @ matrix_remove_bit(31, 128)

    m = matrix_zero(127)
    for i in range(127):
        t = state @ temper
        m[:, i] = t[:, 0]
        state = state @ next_state
    
    return m

def matrix_xoroshiro():
    state = matrix_identity(128)
    s0 = state[:, 64:128]
    s1 = state[:, 0:64] ^ s0

    state[:, 64:128] = s0 @ matrix_rotl(24) ^ s1 ^ s1 @ matrix_lshift(16)
    state[:, 0:64] = s1 @ matrix_rotl(37)
    
    return state

# matrix_inverse(matrix_xoroshiro())
def matrix_xoroshiro_reverse():
    state = matrix_identity(128)
    
    s0 = state[:, 64:128].copy()
    s1 = state[:, 0:64].copy()

    s1 = s1 @ matrix_rotl(27)
    s0 = s0 ^ s1 ^ s1 @ matrix_lshift(16)
    s0 = s0 @ matrix_rotl(40)
    s1 ^= s0

    state[:, 64:128] = s0
    state[:, 0:64] = s1
    
    return state

def matrix_xoroshiro_128_lsb():
    state = matrix_identity(128)
    next_state = matrix_xoroshiro()

    m = matrix_zero(128)
    for i in range(128):
        m[:, i] = state[:, 0] ^ state[:, 64]
        state = state @ next_state

    return m

def matrix_xorshift():
    state = matrix_identity(128)
    s3, s2, s1, s0 = (state[:, i:i+32] for i in range(0, 128, 32))

    t = s0.copy()
    t ^= t @ matrix_lshift(11, 32)
    t ^= t @ matrix_rshift(8, 32)
    t ^= s3 ^ s3 @ matrix_rshift(19, 32)

    state[:, 96:128] = s1
    state[:, 64:96] = s2
    state[:, 32:64] = s3
    state[:, 0:32] = t

    return state

def matrix_xorshift_output():
    pass

def print_matrix_table(mat, n=128, a=4):
    c = 1
    for i in range(n):
        x = mat[:, i]
        y = gf2_to_int(x.tolist())
        print(f"0x{y:032X}", end=", ")
        if c % a == 0:
            print()
        c += 1

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

    inv = matrix_inverse(matrix_tinymt_127_lsb())
    print_matrix_table(inv, 127)