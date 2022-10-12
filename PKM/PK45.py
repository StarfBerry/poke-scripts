import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util import ByteStruct, SIZE_4PARTY, SIZE_4STORED, get_checksum, decrypt_array_45, get_hp_type, get_hp_damage

class PK4(ByteStruct):
    def __init__(self, data):
        if not isinstance(data, bytearray) or len(data) != SIZE_4PARTY:
            raise TypeError("Unsupported type/size.")
        
        self.data = data

        if self.is_encrypted or not self.is_valid:
            self.data = decrypt_array_45(self.data)
        
    @property
    def is_valid(self):
        return self.checksum == get_checksum(self.data, SIZE_4STORED)

    @property
    def is_encrypted(self):
        return self.u32_from_le_bytes(0x64) != 0

    @property
    def pid(self):
        return self.u32_from_le_bytes(0x00)
    
    @property
    def nature(self):
        return self.pid % 25
    
    @property
    def checksum(self):
        return self.u16_from_le_bytes(0x06)

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
    def shiny_xor(self):
        return (self.pid >> 16) ^ (self.pid & 0xffff) ^ self.tid ^ self.sid

    @property
    def is_shiny(self):
        return self.shiny_xor < 8

    @property
    def ot_friendship(self):
        return self.data[0x14]
    
    @property
    def ability(self):
        return self.data[0x15]

    @property
    def language(self):
        return self.data[0x17]

    @property
    def evs(self):
        hp, atk, dfs, spe, spa, spd = (self.data[0x18 + i] for i in range(6))  
        return [hp, atk, dfs, spa, spd, spe]
    
    @property
    def moves(self):
        return [self.u16_from_le_bytes(0x28 + 2*i) for i in range(4)]

    @property
    def pps(self):
        return [self.data[0x30 + i] for i in range(4)]
    
    @property
    def pp_ups(self):
        return [self.data[0x34 + i] for i in range(4)]

    @property
    def iv32(self):
        return self.u32_from_le_bytes(0x38)

    @property
    def ivs(self):
        hp, atk, dfs, spe, spa, spd = ((self.iv32 >> (5*i)) & 31 for i in range(6))  
        return [hp, atk, dfs, spa, spd, spe]

    @property
    def hidden_power_type(self):
        return get_hp_type(self.ivs)
    
    @property
    def hidden_power_dmge(self):
        return get_hp_damage(self.ivs)

    @property
    def is_egg(self):
        return ((self.iv32 >> 30) & 1) == 1

    @property
    def fateful_encounter(self):
        return (self.data[0x40] & 1) == 1

    @property
    def gender(self):
        return (self.data[0x40] >> 1) & 3
    
    @property
    def form(self):
        return self.data[0x40] >> 3
    
    @property
    def shiny_leaf(self):
        return self.data[0x41]

    @property
    def pkrs(self):
        return self.data[0x82]

    @property
    def pkrs_days(self):
        return self.pkrs & 0xF
    
    @property
    def pkrs_strain(self):
        return self.pkrs >> 4

    @property
    def ball_dppt(self):
        return self.data[0x83]
    
    @property
    def ball_hgss(self):
        return self.data[0x86]

    @property
    def status_condition(self):
        return self.u32_from_le_bytes(0x88)

    @property   
    def level(self):
        return self.data[0x8C]
    
    @property
    def stats(self):
        curr_hp, max_hp, atk, dfs, spe, spa, spd = (self.u16_from_le_bytes(0x8E + 2*i) for i in range(7))
        return [curr_hp, max_hp, atk, dfs, spa, spd, spe]

class PK5(PK4):
    @property
    def nature(self):
        return self.data[0x41]
    
    @property
    def hidden_ability(self):
        return (self.data[0x42] & 1) == 1
    
    @property
    def ball(self):
        return self.data[0x83]