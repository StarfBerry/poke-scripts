def lobits(v, b):
    return v & ((1 << b) - 1)
 
def bits(x, start, size):
    return lobits(x >> start, size)

def exbits(x, start, size, b=32):
    return bits(x, start, size) << (b - size)

def bit(x, b):
    return x & (1 << b)

def reverse_lshift_xor_mask(x, shift=1, mask=0xffffffff, b=32):
    for i in range(shift, b, shift):
        x ^= (bits(x, i-shift, shift) & (mask >> i)) << i
    return x

def reverse_rshift_xor_mask(x, shift=1, mask=0xffffffff, b=32):
    for i in range(shift, b, shift):
        x ^= (exbits(x, b-i, shift) & (mask << i)) >> i
    return x

def u8(x):
    return x & 0xff

def u16(x):
    return x & 0xffff

def u32(x):
    return x & 0xffffffff

def u64(x):
    return x & 0xffffffffffffffff

def is_power2(x):
    return x & (x-1) == 0 and x

def u16_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+2], byteorder="little")

def u32_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+4], byteorder="little") 

def u64_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+8], byteorder="little")

def u16_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+2], byteorder="big")

def u32_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+4], byteorder="big") 

def u64_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+8], byteorder="big")