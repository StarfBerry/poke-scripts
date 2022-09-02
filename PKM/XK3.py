import sys
sys.path.append(".")
sys.path.append("../")

from Util import ByteStruct, SIZE_3XSTORED, get_hp_type, get_hp_damage
from PKM import species_id_to_dex_number, species_to_gender_ratio, species_to_abilities, get_hp_type, get_hp_damage

class XK3(ByteStruct):
    def __init__(self, data):
        if not isinstance(data, bytearray) or len(data) != SIZE_3XSTORED:
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
    def held_item(self):
        return self.u16_from_be_bytes(0x02)
    
    @property
    def current_hp(self):
        return self.u16_from_be_bytes(0x04)
    
    @property
    def ot_friendship(self):
        return self.u16_from_be_bytes(0x06)
    
    @property
    def level(self):
        return self.data[0x11]

    @property
    def pkrs_strain(self):
        return self.data[0x13] & 0xF
    
    @property
    def pkrs_days(self):
        return max(self.i8_from_bytes(0x15), 0)
    
    @property
    def is_valid(self):
        return (self.data[0x1D] & 0x20) == 0
    
    @property
    def ability_bit(self):
        return (self.data[0x1D] & 0x40) == 0x40
    
    @property
    def ability(self):
        return species_to_abilities[self.species][self.ability_bit]
    
    @property
    def is_egg(self):
        return (self.data[0x1D] & 0x80) == 0x80
    
    @property
    def sid(self):
        return self.u16_from_be_bytes(0x24)
    
    @property
    def tid(self):
        return self.u16_from_be_bytes(0x26)
    
    @property
    def pid(self):
        return self.u32_from_be_bytes(0x28)
    
    @property
    def nature(self):
        return self.pid % 25
    
    @property
    def shiny_xor(self):
        pid = self.pid
        return (pid >> 16) ^ (pid & 0xffff) ^ self.tid ^ self.sid

    @property
    def is_shiny(self):
        return self.shiny_xor < 8
    
    @property
    def moves(self):
        return [self.u16_from_be_bytes(0x80 + 4*i) for i in range(4)]
    
    @property
    def pps(self):
        return [self.data[0x82 + 4*i] for i in range(4)]
    
    @property
    def stats(self):
        return [self.current_hp] + [self.u16_from_be_bytes(0x90 + 2*i) for i in range(6)]
    
    @property
    def evs(self):
        return [min(255, self.u16_from_be_bytes(0x9C + 2*i)) for i in range(6)]

    @property
    def ivs(self):
        return [self.data[0xA8 + i] for i in range(6)]
    
    @property  
    def hidden_power_type(self):
        return get_hp_type(self.ivs)
    
    @property
    def hidden_power_dmge(self):
        return get_hp_damage(self.ivs)
    
    @property
    def shadow_id(self):
        return self.u16_from_be_bytes(0xBA)