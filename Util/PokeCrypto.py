# Reference: https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/PKM/Util/PokeCrypto.cs

import os, sys
sys.path.append(os.path.dirname(__file__))

from Bytes import u16_from_le_bytes, u32_from_le_bytes

BLOCK_POSITION = (
    0, 1, 2, 3, 0, 1, 3, 2, 0, 2, 1, 3, 0, 3, 1, 2, 0, 2, 3, 1, 0, 3, 2, 1, 1, 0, 2, 3, 1, 0, 3, 2,
    2, 0, 1, 3, 3, 0, 1, 2, 2, 0, 3, 1, 3, 0, 2, 1, 1, 2, 0, 3, 1, 3, 0, 2, 2, 1, 0, 3, 3, 1, 0, 2,
    2, 3, 0, 1, 3, 2, 0, 1, 1, 2, 3, 0, 1, 3, 2, 0, 2, 1, 3, 0, 3, 1, 2, 0, 2, 3, 1, 0, 3, 2, 1, 0,
    # duplicates of 0-7 to eliminate modulus
    0, 1, 2, 3, 0, 1, 3, 2, 0, 2, 1, 3, 0, 3, 1, 2, 0, 2, 3, 1, 0, 3, 2, 1, 1, 0, 2, 3, 1, 0, 3, 2)

BLOCK_POSITION_INVERT = (
    0, 1, 2, 4, 3, 5, 6, 7, 12, 18, 13, 19, 8, 10, 14, 20, 16, 22, 9, 11, 15, 21, 17, 23,
    # duplicates of 0-7 to eliminate modulus
    0, 1, 2, 4, 3, 5, 6, 7)

SIZE_1ULIST = 69
SIZE_1JLIST = 59
SIZE_1PARTY = 44
SIZE_1STORED = 33

SIZE_2ULIST = 73
SIZE_2JLIST = 63
SIZE_2PARTY = 48
SIZE_2STORED = 32
SIZE_2STADIUM = 60

SIZE_3CSTORED = 312
SIZE_3XSTORED = 196
SIZE_3PARTY = 100
SIZE_3STORED = 80
SIZE_3HEADER = 32
SIZE_3BLOCK = 12

SIZE_4PARTY = 236
SIZE_4STORED = 136
SIZE_4BLOCK = 32

SIZE_5PARTY = 220
SIZE_5STORED = 136

SIZE_6PARTY = 260
SIZE_6STORED = 232
SIZE_6BLOCK = 56

SIZE_8PARTY = 344
SIZE_8STORED = 328
SIZE_8BLOCK = 80

SIZE_8APARTY = 376
SIZE_8ASTORED = 360
SIZE_8ABLOCK = 88

def shuffle_array_3(data, sv):
    sdata = data.copy()
    index = sv * 4
    
    for block in range(4):
        i = SIZE_3HEADER + (SIZE_3BLOCK * BLOCK_POSITION[index + block])
        copy = data[i:i+SIZE_3BLOCK]
        j = SIZE_3HEADER + (SIZE_3BLOCK * block)
        sdata[j:j+SIZE_3BLOCK] = copy

    return sdata

def shuffle_array(data, sv, block_size):
    sdata = data.copy()
    index = sv * 4
    start = 8
    
    for block in range(4):
        i = start + (block_size * BLOCK_POSITION[index + block])
        copy = data[i:i+block_size]
        j = start + (block_size * block)
        sdata[j:j+block_size] = copy
    
    return sdata

def crypt_array(data, seed, start, end):
    for i in range(start, end, 2):
        seed = (seed * 0x41c64e6d + 0x6073) & 0xffffffff
        xor = seed >> 16
        data[i] ^= xor & 0xff
        data[i+1] ^= xor >> 8 

def crypt_pkm(data, pv, block_size):
    start = 8
    end = (4 * block_size) + start
    crypt_array(data, pv, start, end)
    if len(data) > end:
        crypt_array(data, pv, end, len(data))

def crypt_pkm_45(data, pv, chk, block_size):
    start = 8
    end = (4 * block_size) + start
    crypt_array(data, chk, start, end)
    if len(data) > end:
        crypt_array(data, pv, end, len(data))

def get_checksum_3(data):
    chk = 0
    span = data[0x20:SIZE_3STORED]
    for i in range(0, len(span), 2):
        chk += u16_from_le_bytes(span, i)
    return chk & 0xFFFF

def get_checksum(data, party_start):
    chk = 0
    span = data[0x08:party_start]
    for i in range(0, len(span), 2):
        chk += u16_from_le_bytes(span, i)
    return chk & 0xffff

def decrypt_array_3(ekm):
    pid = u32_from_le_bytes(ekm, 0x0)
    oid = u32_from_le_bytes(ekm, 0x4)
    seed = pid ^ oid
    
    to_encrypt = ekm[SIZE_3HEADER:SIZE_3STORED]
    for i in range(0, len(to_encrypt), 4):
        chunk = u32_from_le_bytes(to_encrypt, i)
        update = chunk ^ seed
        ofs = SIZE_3HEADER + i
        ekm[ofs:ofs+4] = update.to_bytes(4, "little")

    return shuffle_array_3(ekm, pid % 24)

def encrypt_array_3(pk):
    pid = u32_from_le_bytes(pk, 0x0)
    oid = u32_from_le_bytes(pk, 0x4)
    seed = pid ^ oid

    ekm = shuffle_array_3(pk, BLOCK_POSITION_INVERT[pid % 24])

    to_encrypt = ekm[SIZE_3HEADER:SIZE_3STORED]
    for i in range(0, len(to_encrypt), 4):
        chunk = u32_from_le_bytes(to_encrypt, i)
        update = chunk ^ seed
        ofs = SIZE_3HEADER + i
        ekm[ofs:ofs+4] = update.to_bytes(4, "little")
    
    return ekm

def decrypt_array_45(ekm):
    pv = u32_from_le_bytes(ekm, 0)
    chk = u16_from_le_bytes(ekm, 6)
    sv = (pv >> 13) & 31

    crypt_pkm_45(ekm, pv, chk, SIZE_4BLOCK)
    return shuffle_array(ekm, sv, SIZE_4BLOCK)

def encrypt_array_45(pk):
    pv = u32_from_le_bytes(pk, 0)
    chk = u16_from_le_bytes(pk, 6)
    sv = (pv >> 13) & 31
    
    ekm = shuffle_array(pk, BLOCK_POSITION_INVERT[sv], SIZE_4BLOCK)
    crypt_pkm_45(ekm, pv, chk, SIZE_4BLOCK)
    return ekm

def decrypt_array_67(ekm):
    pv = u32_from_le_bytes(ekm, 0)
    sv = (pv >> 13) & 31

    crypt_pkm(ekm, pv, SIZE_6BLOCK)
    return shuffle_array(ekm, sv, SIZE_6BLOCK)

def encrypt_array_67(pk):
    pv = u32_from_le_bytes(pk, 0)
    sv = (pv >> 13) & 31

    ekm = shuffle_array(pk, BLOCK_POSITION_INVERT[sv], SIZE_6BLOCK)
    crypt_pkm(ekm, pv, SIZE_6BLOCK)
    return ekm

def decrypt_array_89(ekm):
    pv = u32_from_le_bytes(ekm, 0)
    sv = (pv >> 13) & 31

    crypt_pkm(ekm, pv, SIZE_8BLOCK)
    return shuffle_array(ekm, sv, SIZE_8BLOCK)

def encrypt_array_89(pk):
    pv = u32_from_le_bytes(pk, 0)
    sv = (pv >> 13) & 31

    ekm = shuffle_array(pk, BLOCK_POSITION_INVERT[sv], SIZE_8BLOCK)
    crypt_pkm(ekm, pv, SIZE_8BLOCK)
    return ekm

def decrypt_array_8_arceus(ekm):
    pv = u32_from_le_bytes(ekm, 0)
    sv = (pv >> 13) & 31

    crypt_pkm(ekm, pv, SIZE_8ABLOCK)
    return shuffle_array(ekm, sv, SIZE_8ABLOCK)

def encrypt_array_8_arceus(pk):
    pv = u32_from_le_bytes(pk, 0)
    sv = (pv >> 13) & 31

    ekm = shuffle_array(pk, BLOCK_POSITION_INVERT[sv], SIZE_8ABLOCK)
    crypt_pkm(ekm, pv, SIZE_8ABLOCK)
    return ekm