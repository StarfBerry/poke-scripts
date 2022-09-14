import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util import ByteStruct, SIZE_8PARTY, SIZE_8STORED, decrypt_array_8, get_checksum, get_hp_type

class PK8(ByteStruct):
    def __init__(self, data):
        if not isinstance(data, bytearray) or len(data) != SIZE_8PARTY:
            raise TypeError("Unsupported type/size.")
        
        self.data = data

        if self.is_encrypted or not self.is_valid:
            self.data = decrypt_array_8(self.data)
    
    @property
    def ec(self):
        return self.u32_from_le_bytes(0x00)
    
    @property
    def checksum(self):
        return self.u16_from_le_bytes(0x06)
    
    @property
    def is_encrypted(self):
        return self.u16_from_le_bytes(0x70) != 0 or self.u16_from_le_bytes(0x110) != 0
    
    @property
    def is_valid(self):
        return self.u16_from_le_bytes(0x04) == 0 and self.checksum == get_checksum(self.data, SIZE_8STORED)
    
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
        return self.u16_from_le_bytes(0x14)
    
    @property
    def ability_number(self):
        return self.data[0x16] & 7
    
    @property
    def can_gigantamax(self):
        return (self.data[0x16] & 16) != 0
    
    @property
    def mark_value(self):
        return self.u16_from_le_bytes(0x18)
    
    @property
    def pid(self):
        return self.u32_from_le_bytes(0x1C)
    
    @property
    def shiny_xor(self):
        return (self.pid >> 16) ^ (self.pid & 0xffff) ^ self.tid ^ self.sid
    
    @property
    def is_shiny(self):
        return self.shiny_xor < 16

    @property
    def nature(self):
        return self.data[0x20]
    
    @property
    def stat_nature(self):
        return self.data[0x21]
    
    @property
    def fateful_encounter(self):
        return (self.data[0x22] & 1) == 1
    
    @property
    def gender(self):
        return (self.data[0x22] >> 2) & 0x3
    
    @property
    def form(self):
        return self.data[0x24]
    
    @property
    def evs(self):
        hp, atk, dfs, spe, spa, spd = (self.data[0x26 + i] for i in range(6))
        return [hp, atk, dfs, spa, spd, spe]
    
    @property
    def pkrs(self):
        return self.data[0x32]
    
    @property
    def pkrs_days(self):
        return self.pkrs & 0xf
    
    @property
    def pkrs_strain(self):
        return self.pkrs >> 4
    
    @property
    def height(self):
        return self.data[0x50]
    
    @property
    def weight(self):
        return self.data[0x51]
    
    @property
    def moves(self):
        return [self.u16_from_le_bytes(0x72 + 2*i) for i in range(4)]
    
    @property
    def pps(self):
        return [self.data[0x7A + i] for i in range(4)]
    
    @property
    def pp_ups(self):
        return [self.data[0x7E + i] for i in range(4)]
    
    @property
    def current_hp(self):
        return self.u16_from_le_bytes(0x8A)
    
    @property
    def iv32(self):
        return self.u32_from_le_bytes(0x8C)
    
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
    def dynamax_level(self):
        return self.data[0x90]
    
    @property
    def status_condition(self):
        return self.u32_from_le_bytes(0x94)
    
    @property
    def language(self):
        return self.data[0xE2]

    @property
    def ot_friendship(self):
        return self.data[0x112]
    
    @property
    def ball(self):
        return self.data[0x124]

    @property
    def level(self):
        return self.data[0x148]
    
    @property
    def stats(self):
        max_hp, atk, dfs, spe, spa, spd = (self.u16_from_le_bytes(0x14A + 2*i) for i in range(6))
        return [self.current_hp, max_hp, atk, dfs, spa, spd, spe]