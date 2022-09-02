def u16_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+2], byteorder="little")

def i16_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+2], byteorder="little", signed=True)

def u32_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+4], byteorder="little")

def i32_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+4], byteorder="little", signed=True)

def u64_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+8], byteorder="little")

def i64_from_le_bytes(data, start):
    return int.from_bytes(data[start:start+8], byteorder="little", signed=True)

def i8_from_bytes(data, start):
    return int.from_bytes(data[start:start+1], byteorder="big", signed=True)

def u16_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+2], byteorder="big")

def i16_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+2], byteorder="big", signed=True)

def u32_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+4], byteorder="big") 

def i32_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+4], byteorder="big", signed=True)

def u64_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+8], byteorder="big")

def i64_from_be_bytes(data, start):
    return int.from_bytes(data[start:start+8], byteorder="big", signed=True)