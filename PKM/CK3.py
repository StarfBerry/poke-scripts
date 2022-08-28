import sys
sys.path.append(".")
sys.path.append("../")

from Util import SIZE_3CSTORED, u16_from_be_bytes, u32_from_be_bytes, i32_from_be_bytes, i8_from_bytes, get_hp_type, get_hp_damage
from PKM import species_id_to_dex_number, species_to_gender_ratio, species_to_abilities

class CK3:
    def __init__(self, data):
        if not isinstance(data, bytearray) or len(data) != SIZE_3CSTORED:
            raise TypeError("Unsupported file type/size.")
        
        self.data = data

        self.pid = u32_from_be_bytes(self.data, 0x04)
        self.sid = u16_from_be_bytes(self.data, 0x14)
        self.tid = u16_from_be_bytes(self.data, 0x16)

        self.ivs = self.all_ivs()

    def is_shiny(self):
        return ((self.pid >> 16) ^ (self.pid & 0xffff) ^ self.tid ^ self.sid) < 8
    
    def nature(self):
        return self.pid % 25

    def species_id(self):
        return u16_from_be_bytes(self.data, 0x00)
    
    def species(self):
        return species_id_to_dex_number[self.species_id()]
    
    def gender(self):
        gr = species_to_gender_ratio[self.species()]
        if gr == 255:
            return 2 # genderless
        elif gr == 254:
            return 1 # female only
        elif gr == 0:
            return 0 # male only
        return 1 if (self.pid & 0xff) < gr else 0

    def level(self):
        return self.data[0x60]
    
    def move1(self):
        return u16_from_be_bytes(self.data, 0x78)
    
    def move1_pp(self):
        return self.data[0x7A]
    
    def move2(self):
        return u16_from_be_bytes(self.data, 0x7C)
    
    def move2_pp(self):
        return self.data[0x7E]

    def move3(self):
        return u16_from_be_bytes(self.data, 0x80)
    
    def move3_pp(self):
        return self.data[0x82]
    
    def move4(self):
        return u16_from_be_bytes(self.data, 0x84)
    
    def move4_pp(self):
        return self.data[0x86]
    
    def held_item(self):
        return u16_from_be_bytes(self.data, 0x88)
    
    def stat_current_hp(self):
        return u16_from_be_bytes(self.data, 0x8A)
    
    def stat_max_hp(self):
        return u16_from_be_bytes(self.data, 0x8C)
    
    def stat_atk(self):
        return u16_from_be_bytes(self.data, 0x8E)
    
    def stat_def(self):
        return u16_from_be_bytes(self.data, 0x90)
    
    def stat_spa(self):
        return u16_from_be_bytes(self.data, 0x92)
    
    def stat_spd(self):
        return u16_from_be_bytes(self.data, 0x94)
    
    def stat_spe(self):
        return u16_from_be_bytes(self.data, 0x96)
    
    def ev_hp(self):
        return min(255, u16_from_be_bytes(self.data, 0x98))
    
    def ev_atk(self):
        return min(255, u16_from_be_bytes(self.data, 0x9A))
    
    def ev_def(self):
        return min(255, u16_from_be_bytes(self.data, 0x9C))
    
    def ev_spa(self):
        return min(255, u16_from_be_bytes(self.data, 0x9E))
    
    def ev_spd(self):
        return min(255, u16_from_be_bytes(self.data, 0xA0))
    
    def ev_spe(self):
        return min(255, u16_from_be_bytes(self.data, 0xA2))
    
    def iv_hp(self):
        return min(31, u16_from_be_bytes(self.data, 0xA4))
    
    def iv_atk(self):
        return min(31, u16_from_be_bytes(self.data, 0xA6))
    
    def iv_def(self):
        return min(31, u16_from_be_bytes(self.data, 0xA8))
    
    def iv_spa(self):
        return min(31, u16_from_be_bytes(self.data, 0xAA))
    
    def iv_spd(self):
        return min(31, u16_from_be_bytes(self.data, 0xAC))
    
    def iv_spe(self):
        return min(31, u16_from_be_bytes(self.data, 0xAE))
    
    def all_ivs(self):
        ivs = [0] * 6
        ivs[0] = self.iv_hp()
        ivs[1] = self.iv_atk()
        ivs[2] = self.iv_def()
        ivs[3] = self.iv_spa()
        ivs[4] = self.iv_spd()
        ivs[5] = self.iv_spe()        
        return ivs
    
    def hidden_power_type(self):
        return get_hp_type(self.ivs)
    
    def hidden_power_dmge(self):
        return get_hp_damage(self.ivs)
    
    def ot_friendship(self):
        return min(255, u16_from_be_bytes(self.data, 0xB0))
    
    def pkrs_strain(self):
        return self.data[0xCA] & 0xF
    
    def is_egg(self):
        return self.data[0xCB] == 1
    
    def ability_bit(self):
        return self.data[0xCC] == 1
    
    def ability(self):
        return species_to_abilities[self.species()][self.ability_bit()]
    
    def pkrs_days(self):
        d = i8_from_bytes(self.data, 0xD0)
        return max(d, 0)
    
    def shadow_id(self):
        return u16_from_be_bytes(self.data, 0xD8)
    
    def purification(self):
        return i32_from_be_bytes(self.data, 0xDC)
    
    def is_shadow(self):
        return self.shadow_id() != 0 and self.purification() != -100