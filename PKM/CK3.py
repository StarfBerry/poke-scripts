import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util import ByteStruct, SIZE_3CSTORED, get_hp_type, get_hp_damage
from PKM.PK3 import species_id_to_dex_number, species_to_gender_ratio, species_to_abilities

class CK3(ByteStruct):
    def __init__(self, data):
        if not isinstance(data, bytearray) or len(data) != SIZE_3CSTORED:
            raise TypeError("Unsupported type/size.")
        
        self.data = data

    @property
    def species_id(self):
        return self.u16_from_be_bytes(0x00)
    
    @property
    def species(self):
        return species_id_to_dex_number[self.species_id]
    
    @property
    def gender(self):
        gr = species_to_gender_ratio[self.species]
        if gr == 255:
            return 2 # genderless
        elif gr == 254:
            return 1 # female only
        elif gr == 0:
            return 0 # male only
        return 1 if (self.pid & 0xff) < gr else 0

    @property
    def pid(self):
        return self.u32_from_be_bytes(0x04)
    
    @property
    def nature(self):
        return self.pid % 25
        
    @property
    def language(self):
        return self.data[0x0B]
    
    @property
    def ball(self):
        return self.data[0x0F]
    
    @property
    def sid(self):
        return self.u16_from_be_bytes(0x14)
    
    @property
    def tid(self):
        return self.u16_from_be_bytes(0x16)

    @property
    def shiny_xor(self):
        return (self.pid >> 16) ^ (self.pid & 0xffff) ^ self.tid ^ self.sid

    @property
    def is_shiny(self):
        return self.shiny_xor < 8

    @property
    def level(self):
        return self.data[0x60]
    
    @property
    def moves(self):
        return [self.u16_from_be_bytes(0x78 + 4*i) for i in range(4)]

    @property
    def pps(self):
        return [self.data[0x7A + 4*i] for i in range(4)]
    
    @property
    def pp_ups(self):
        return [self.data[0x7B + 4*i] for i in range(4)]

    @property
    def held_item(self):
        return self.u16_from_be_bytes(0x88)
    
    @property
    def stats(self):
        return [self.u16_from_be_bytes(0x8A + 2*i) for i in range(7)]

    @property
    def evs(self):
        return [min(255, self.u16_from_be_bytes(0x98 + 2*i)) for i in range(6)]
    
    @property
    def ivs(self):
        return [min(31, self.u16_from_be_bytes(0xA4 + 2*i)) for i in range(6)]

    @property  
    def hidden_power_type(self):
        return get_hp_type(self.ivs)
    
    @property
    def hidden_power_dmge(self):
        return get_hp_damage(self.ivs)
    
    @property
    def ot_friendship(self):
        return min(255, self.u16_from_be_bytes(0xB0))
    
    @property
    def fateful_encounter(self):
        return ((self.data[0xC9] >> 4) & 1) == 1

    @property
    def pkrs_strain(self):
        return self.data[0xCA] & 0xF
    
    @property
    def is_egg(self):
        return self.data[0xCB] == 1
    
    @property
    def ability_bit(self):
        return self.data[0xCC] == 1
    
    @property
    def ability(self):
        return species_to_abilities[self.species][self.ability_bit]
    
    @property
    def is_valid(self):
        return self.data[0xCD] == 0

    @property
    def pkrs_days(self):
        return max(self.i8_from_bytes(0xD0), 0)
    
    @property
    def shadow_id(self):
        return self.u16_from_be_bytes(0xD8)
    
    @property
    def purification(self):
        return self.i32_from_be_bytes(0xDC)
    
    @property
    def is_shadow(self):
        return self.shadow_id != 0 and self.purification != -100