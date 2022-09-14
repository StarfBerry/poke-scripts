def u8(x):
    return x & 0xff

def u16(x):
    return x & 0xffff

def u32(x):
    return x & 0xffffffff

def u64(x):
    return x & 0xffffffffffffffff

def lobits(x, b):
    return x & ((1 << b) - 1)
 
def bits(x, start, size):
    return lobits(x >> start, size)

def exbits(x, start, size, b=32):
    return bits(x, start, size) << (b - size)

def reverse_lshift_xor_mask(x, shift=1, mask=0xffffffff, b=32):
    for i in range(shift, b, shift):
        x ^= (bits(x, i-shift, shift) & (mask >> i)) << i
    return x

def reverse_rshift_xor_mask(x, shift=1, mask=0xffffffff, b=32):
    for i in range(shift, b, shift):
        x ^= (exbits(x, b-i, shift) & (mask << i)) >> i
    return x

def is_power2(x):
    return x & (x-1) == 0 and x != 0

def change_endian(x):
    x = ((x << 8) & 0xFF00FF00) | ((x >> 8) & 0xFF00FF)
    return ((x & 0xffff) << 16) | (x >> 16)

def change_endian_64(x):
    a = change_endian(x & 0xffffffff)
    b = change_endian(x >> 32)
    return (a << 32) | b