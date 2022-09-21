def u8(x):
    return x & 0xff

def u16(x):
    return x & 0xffff

def u32(x):
    return x & 0xffffffff

def u64(x):
    return x & 0xffffffffffffffff

# reverse x ^= (x << shift) & mask
def reverse_lshift_xor_mask(x, shift=1, mask=0xffffffff):
    m = (1 << shift) - 1
    for i in range(shift, 32, shift):
        tmp = (x >> (i - shift)) & m
        x ^= (tmp & (mask >> i)) << i
    return x

# reverse x ^= (x >> shift) & mask
def reverse_rshift_xor_mask(x, shift=1, mask=0xffffffff):
    m = (1 << shift) - 1
    s = 32 - shift
    for i in range(shift, 32, shift):
        tmp = ((x >> (32 - i)) & m) << s
        x ^= (tmp & (mask << i)) >> i
    return x

def reverse_lshift_xor_mask_64(x, shift=1, mask=0xffffffffffffffff):
    m = (1 << shift) - 1
    for i in range(shift, 64, shift):
        tmp = (x >> (i - shift)) & m
        x ^= (tmp & (mask >> i)) << i
    return x

def reverse_rshift_xor_mask_64(x, shift=1, mask=0xffffffffffffffff):
    m = (1 << shift) - 1
    s = 64 - shift
    for i in range(shift, 64, shift):
        tmp = ((x >> (64 - i)) & m) << s
        x ^= (tmp & (mask << i)) >> i
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

# lsb at index 0
def bits_to_int(bits):
    return sum(bits[i] << i for i in range(len(bits)))

def bits_to_ints(bits, size=32):
    return [bits_to_int(bits[i*size:(i+1)*size]) for i in range(len(bits) // size)]