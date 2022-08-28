import sys
sys.path.append(".")
sys.path.append("../")

from Util import SIZE_4PARTY, SIZE_4STORED, get_checksum, decrypt_array_45, u16_from_le_bytes, u32_from_le_bytes, get_hp_type, get_hp_damage

class PK4:
    def __init__(self, data, decrypted=False):
        if not isinstance(data, bytearray) or len(data) != SIZE_4PARTY:
            raise TypeError("Unsupported file type/size.")
        
        if not decrypted:
            data = decrypt_array_45(data)
        
        self.data = data

        if self.checksum() != get_checksum(self.data, SIZE_4STORED):
            raise ValueError("Invalid checksum.")
        
        self.pid = u32_from_le_bytes(self.data, 0x00)
        self.tid = u16_from_le_bytes(self.data, 0x0C)
        self.sid = u16_from_le_bytes(self.data, 0x0E)
        self.iv32 = u32_from_le_bytes(self.data, 0x38)
        self.pkrs = self.data[0x82]

        self.ivs = self.all_ivs()

    def is_shiny(self):
        return ((self.pid >> 16) ^ (self.pid & 0xffff) ^ self.tid ^ self.sid) < 8
    
    def nature(self):
        return self.pid % 25
    
    def checksum(self):
        return u16_from_le_bytes(self.data, 0x06)

    def species(self):
        return u16_from_le_bytes(self.data, 0x08)
    
    def held_item(self):
        return u16_from_le_bytes(self.data, 0x0A)
    
    def ot_friendship(self):
        return self.data[0x14]
    
    def ability(self):
        return self.data[0x15]
    
    def ev_hp(self):
        return self.data[0x18]
    
    def ev_atk(self):
        return self.data[0x19]
    
    def ev_def(self): 
        return self.data[0x1A]
    
    def ev_spe(self):
        return self.data[0x1B]
    
    def ev_spa(self):
        return self.data[0x1C]
    
    def ev_spd(self):
        return self.data[0x1D]

    def move1(self):
        return u16_from_le_bytes(self.data, 0x28)
    
    def move2(self):
        return u16_from_le_bytes(self.data, 0x2A)
    
    def move3(self):
        return u16_from_le_bytes(self.data, 0x2C)
    
    def move4(self):
        return u16_from_le_bytes(self.data, 0x2E)

    def move1_pp(self):
        return self.data[0x30]
    
    def move2_pp(self):
        return self.data[0x31]
    
    def move3_pp(self):
        return self.data[0x32]
    
    def move4_pp(self):
        return self.data[0x33]
    
    def iv_hp(self):
        return self.iv32 & 0x1F
    
    def iv_atk(self):
        return (self.iv32 >> 5) & 0x1F
    
    def iv_def(self):
        return (self.iv32 >> 10) & 0x1F
    
    def iv_spe(self):
        return (self.iv32 >> 15) & 0x1F

    def iv_spa(self):
        return (self.iv32 >> 20) & 0x1F

    def iv_spd(self):
        return (self.iv32 >> 25) & 0x1F
    
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

    def is_egg(self):
        return ((self.iv32 >> 30) & 1) == 1

    def gender(self):
        return (self.data[0x40] >> 1) & 3
    
    def form(self):
        return self.data[0x40] >> 3

    def pkrs_days(self):
        return self.pkrs & 0xF
    
    def pkrs_strain(self):
        return self.pkrs >> 4
       
    def level(self):
        return self.data[0x8C]
    
    def stat_current_hp(self):
        return u16_from_le_bytes(self.data, 0x8E)
    
    def stat_max_hp(self):
        return u16_from_le_bytes(self.data, 0x90)
    
    def stat_atk(self):
        return u16_from_le_bytes(self.data, 0x92)
    
    def stat_def(self):
        return u16_from_le_bytes(self.data, 0x94)
    
    def stat_spe(self):
        return u16_from_le_bytes(self.data, 0x96)
    
    def stat_spa(self):
        return u16_from_le_bytes(self.data, 0x98)
    
    def stat_spd(self):
        return u16_from_le_bytes(self.data, 0x9A)

class PK5(PK4):
    def __init__(self, data, decrypted=False):
        super().__init__(data, decrypted)
    
    def nature(self):
        return self.data[0x41]
    
    def hidden_ability(self):
        return (self.data[0x42] & 1) == 1