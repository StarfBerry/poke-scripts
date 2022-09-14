import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util import ByteStruct, SIZE_6PARTY, SIZE_6STORED, decrypt_array_67, get_checksum, get_hp_type

class PK6(ByteStruct):
    def __init__(self, data):
        if not isinstance(data, bytearray) or len(data) != SIZE_6PARTY:
            raise TypeError("Unsupported type/size.")
        
        self.data = data

        if self.is_encrypted or not self.is_valid:
            self.data = decrypt_array_67(self.data)
    
    @property
    def ec(self):
        return self.u32_from_le_bytes(0x00)

    @property
    def checksum(self):
        return self.u16_from_le_bytes(0x06)
    
    @property
    def is_valid(self):
        return self.checksum == get_checksum(self.data, SIZE_6STORED)
    
    @property
    def is_encrypted(self):
        return self.u16_from_le_bytes(0xC8) != 0 or self.u16_from_le_bytes(0x58) != 0

    @property
    def species(self):
        return self.u16_from_le_bytes(0x08)

    @property
    def held_item(self):
        return self.u16_from_le_bytes(0x0A)
    
    @property
    def tid(self):
        return self.u16_from_le_bytes(0x0C)
    
    @property
    def sid(self):
        return self.u16_from_le_bytes(0x0E)
    
    @property
    def ability(self):
        return self.data[0x14]
    
    @property
    def ability_number(self):
        return self.data[0x15]
    
    @property
    def pid(self):
        return self.u32_from_le_bytes(0x18)
    
    @property
    def shiny_xor(self):
        return (self.pid >> 16) ^ (self.pid & 0xffff) ^ self.tid ^ self.sid

    @property
    def is_shiny(self):
        return self.shiny_xor < 16
    
    @property
    def nature(self):
        return self.data[0x1C]
    
    @property
    def fateful_encounter(self):
        return (self.data[0x1D] & 1) == 1
    
    @property
    def gender(self):
        return (self.data[0x1D] >> 1) & 3
    
    @property
    def form(self):
        return self.data[0x1D] >> 3
    
    @property
    def evs(self):
        hp, atk, dfs, spe, spa, spd = (self.data[0x1E + i] for i in range(6))  
        return [hp, atk, dfs, spa, spd, spe]

    @property
    def pkrs(self):
        return self.data[0x2B]
    
    @property
    def pkrs_days(self):
        return self.pkrs & 0xF
    
    @property
    def pkrs_strain(self):
        return self.pkrs >> 4
    
    @property
    def moves(self):
        return [self.u16_from_le_bytes(0x5A + 2*i) for i in range(4)]

    @property
    def pps(self):
        return [self.data[0x62 + i] for i in range(4)]
    
    @property
    def pp_ups(self):
        return [self.data[0x66 + i] for i in range(4)]

    @property
    def iv32(self):
        return self.u32_from_le_bytes(0x74)

    @property
    def ivs(self):
        hp, atk, dfs, spe, spa, spd = ((self.iv32 >> (5*i)) & 31 for i in range(6))  
        return [hp, atk, dfs, spa, spd, spe]
    
    @property
    def hidden_power_type(self):
        return get_hp_type(self.ivs)

    @property
    def is_egg(self):
        return ((self.iv32 >> 30) & 1) == 1

    @property
    def ot_friendship(self):
        return self.data[0xCA]
    
    @property
    def ball(self):
        return self.data[0xDC]
    
    @property
    def language(self):
        return self.data[0xE3]

    @property
    def status_condition(self):
        return self.u32_from_le_bytes(0xE8)

    @property
    def level(self):
        return self.data[0xEC]
    
    @property
    def stats(self):
        curr_hp, max_hp, atk, dfs, spe, spa, spd = (self.u16_from_le_bytes(0xF0 + 2*i) for i in range(7))
        return [curr_hp, max_hp, atk, dfs, spa, spd, spe]

class PK7(PK6):
    def __init__(self, data):
        super().__init__(data)

class PB7(PK6):
    pass