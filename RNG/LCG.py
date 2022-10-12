class LCRNG:   
    MASK = 0xFFFFFFFF
    BITS = 32
    
    MUL = (
        0x41C64E6D, 0xC2A29A69, 0xEE067F11, 0xCFDDDF21, 0x5F748241, 0x8B2E1481, 0x76006901, 0x1711D201, 
        0xBE67A401, 0xDDDF4801, 0x3FFE9001, 0x90FD2001, 0x65FA4001, 0xDBF48001, 0xF7E90001, 0xEFD20001, 
        0xDFA40001, 0xBF480001, 0x7E900001, 0xFD200001, 0xFA400001, 0xF4800001, 0xE9000001, 0xD2000001, 
        0xA4000001, 0x48000001, 0x90000001, 0x20000001, 0x40000001, 0x80000001, 0x00000001, 0x00000001)
    
    ADD = (
        0x00006073, 0xE97E7B6A, 0x31B0DDE4, 0x67DBB608, 0xCBA72510, 0x1D29AE20, 0xBA84EC40, 0x79F01880, 
        0x08793100, 0x6B566200, 0x803CC400, 0xA6B98800, 0xE6731000, 0x30E62000, 0xF1CC4000, 0x23988000, 
        0x47310000, 0x8E620000, 0x1CC40000, 0x39880000, 0x73100000, 0xE6200000, 0xCC400000, 0x98800000, 
        0x31000000, 0x62000000, 0xC4000000, 0x88000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000)

    def __init__(self, seed=0):         
        self._state = seed & self.MASK

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, seed):
        self._state = seed & self.MASK   

    def next(self):
        self._state = (self._state * self.MUL[0] + self.ADD[0]) & self.MASK
        return self._state

    def rand(self, lim=0):
        rnd = self.next() >> 16
        return rnd % lim if lim else rnd

    def advance(self, n=1):              
        i = 0
        
        while n and i < self.BITS:
            if n & 1:
                self._state = (self._state * self.MUL[i] + self.ADD[i]) & self.MASK
            
            n >>= 1
            i += 1
        
        return self._state
           
    @classmethod
    def calc_distance(cls, s1, s2):
        x, p, i, d = s1 ^ s2, 1, 0, 0       
        
        while x and i < cls.BITS:
            if x & p:
                s1 = (s1 * cls.MUL[i] + cls.ADD[i]) & cls.MASK
                x = s1 ^ s2
                d += p
            
            p <<= 1
            i += 1
        
        return d           
      
class LCRNGR(LCRNG):    
    MUL = (
        0xEEB9EB65, 0xDC6C95D9, 0xBECE51F1, 0xB61664E1, 0x6A6C8DC1, 0xBD562B81, 0xBC109701, 0xB1322E01, 
        0x62A85C01, 0xA660B801, 0xD1017001, 0xB302E001, 0xAA05C001, 0x640B8001, 0x08170001, 0x102E0001, 
        0x205C0001, 0x40B80001, 0x81700001, 0x02E00001, 0x05C00001, 0x0B800001, 0x17000001, 0x2E000001, 
        0x5C000001, 0xB8000001, 0x70000001, 0xE0000001, 0xC0000001, 0x80000001, 0x00000001, 0x00000001)
    
    ADD = (
        0x0A3561A1, 0x4D3CB126, 0x7CD1F85C, 0x9019E2F8, 0x24D33EF0, 0x2EFFE1E0, 0x1A2153C0, 0x18A8E780, 
        0x41EACF00, 0xBE399E00, 0x26033C00, 0xF2467800, 0x7D8CF000, 0x5F19E000, 0x4E33C000, 0xDC678000, 
        0xB8CF0000, 0x719E0000, 0xE33C0000, 0xC6780000, 0x8CF00000, 0x19E00000, 0x33C00000, 0x67800000, 
        0xCF000000, 0x9E000000, 0x3C000000, 0x78000000, 0xF0000000, 0xE0000000, 0xC0000000, 0x80000000)

class MRNG(LCRNG):   
    ADD = (
        0x00003039, 0xD3DC167E, 0xD6651C2C, 0xCD1DCF18, 0x65136930, 0x642B7E60, 0x1935ACC0, 0xB6461980, 
        0x1EF73300, 0x1F9A6600, 0x85E4CC00, 0x26899800, 0xB8133000, 0x1C266000, 0xE84CC000, 0x90998000, 
        0x21330000, 0x42660000, 0x84CC0000, 0x09980000, 0x13300000, 0x26600000, 0x4CC00000, 0x99800000, 
        0x33000000, 0x66000000, 0xCC000000, 0x98000000, 0x30000000, 0x60000000, 0xC0000000, 0x80000000)
    
    def rand15(self):
        return (self.next() >> 16) & 0x7fff

class MRNGR(MRNG, LCRNGR):   
    ADD = (
        0xFC77A683, 0x8C319932, 0xD97E8E94, 0x37D79BE8, 0xDB2E42D0, 0xE39B31A0, 0x71E51340, 0x3624E680, 
        0x92B4CD00, 0xA7159A00, 0x94DB3400, 0x44766800, 0xF3ECD000, 0x93D9A000, 0xD7B34000, 0x6F668000, 
        0xDECD0000, 0xBD9A0000, 0x7B340000, 0xF6680000, 0xECD00000, 0xD9A00000, 0xB3400000, 0x66800000, 
        0xCD000000, 0x9A000000, 0x34000000, 0x68000000, 0xD0000000, 0xA0000000, 0x40000000, 0x80000000)

class GCRNG(LCRNG):    
    MUL = (
        0x000343FD, 0xA9FC6809, 0xDDFF5051, 0xF490B9A1, 0x43BA1741, 0xD290BE81, 0x82E3BD01, 0xBF507A01, 
        0xF8C4F401, 0x7A19E801, 0x1673D001, 0xB5E7A001, 0x8FCF4001, 0xAF9E8001, 0x9F3D0001, 0x3E7A0001, 
        0x7CF40001, 0xF9E80001, 0xF3D00001, 0xE7A00001, 0xCF400001, 0x9E800001, 0x3D000001, 0x7A000001, 
        0xF4000001, 0xE8000001, 0xD0000001, 0xA0000001, 0x40000001, 0x80000001, 0x00000001, 0x00000001)
    
    ADD = (
        0x00269EC3, 0x1E278E7A, 0x098520C4, 0x7E1DBEC8, 0x3E314290, 0x824E1920, 0x844E8240, 0xFD864480, 
        0xDFB18900, 0xD9F71200, 0x5E3E2400, 0x65BC4800, 0x70789000, 0x74F12000, 0x39E24000, 0xB3C48000, 
        0x67890000, 0xCF120000, 0x9E240000, 0x3C480000, 0x78900000, 0xF1200000, 0xE2400000, 0xC4800000, 
        0x89000000, 0x12000000, 0x24000000, 0x48000000, 0x90000000, 0x20000000, 0x40000000, 0x80000000)

class GCRNGR(LCRNG):    
    MUL = (
        0xB9B33155, 0xE05FA639, 0x8A3BF8B1, 0x672D6A61, 0xA04E78C1, 0x0E918181, 0x11A54301, 0x92D38601, 
        0x4FCB0C01, 0xA8261801, 0x728C3001, 0x6E186001, 0x0030C001, 0x90618001, 0x60C30001, 0xC1860001, 
        0x830C0001, 0x06180001, 0x0C300001, 0x18600001, 0x30C00001, 0x61800001, 0xC3000001, 0x86000001, 
        0x0C000001, 0x18000001, 0x30000001, 0x60000001, 0xC0000001, 0x80000001, 0x00000001, 0x00000001)
    
    ADD = (
        0xA170F641, 0x03882AD6, 0x3E0A787C, 0xE493E638, 0xBDC95170, 0x00DC36E0, 0xBC5ABDC0, 0x451EBB80, 
        0x2AE27700, 0x5058EE00, 0x4B01DC00, 0x3F43B800, 0x23877000, 0xDB0EE000, 0x061DC000, 0x4C3B8000, 
        0x98770000, 0x30EE0000, 0x61DC0000, 0xC3B80000, 0x87700000, 0x0EE00000, 0x1DC00000, 0x3B800000, 
        0x77000000, 0xEE000000, 0xDC000000, 0xB8000000, 0x70000000, 0xE0000000, 0xC0000000, 0x80000000)

class ARNG(LCRNG):    
    MUL = (
        0x6C078965, 0x054341D9, 0x0285E9F1, 0xAE3294E1, 0x5A78EDC1, 0x75BEEB81, 0x56221701, 0xCA552E01, 
        0x28EE5C01, 0x82ECB801, 0xCA197001, 0xA532E001, 0x8E65C001, 0x2CCB8001, 0x99970001, 0x332E0001, 
        0x665C0001, 0xCCB80001, 0x99700001, 0x32E00001, 0x65C00001, 0xCB800001, 0x97000001, 0x2E000001, 
        0x5C000001, 0xB8000001, 0x70000001, 0xE0000001, 0xC0000001, 0x80000001, 0x00000001, 0x00000001)
    
    ADD = (
        0x00000001, 0x6C078966, 0xDBFFE6DC, 0x895277F8, 0xE69948F0, 0x392F75E0, 0x778E7BC0, 0xABBB3780, 
        0x68EF6F00, 0x0FC2DE00, 0xD715BC00, 0x8C6B7800, 0x91D6F000, 0x07ADE000, 0x9F5BC000, 0x7EB78000, 
        0xFD6F0000, 0xFADE0000, 0xF5BC0000, 0xEB780000, 0xD6F00000, 0xADE00000, 0x5BC00000, 0xB7800000, 
        0x6F000000, 0xDE000000, 0xBC000000, 0x78000000, 0xF0000000, 0xE0000000, 0xC0000000, 0x80000000)

class ARNGR(LCRNG):
    MUL = (
        0x9638806D, 0x2C1D2E69, 0xA433E711, 0xA955AF21, 0x55B82241, 0x6C055481, 0x40EEE901, 0x91EED201, 
        0x4821A401, 0x41534801, 0x46E69001, 0x9ECD2001, 0x819A4001, 0x13348001, 0x66690001, 0xCCD20001, 
        0x99A40001, 0x33480001, 0x66900001, 0xCD200001, 0x9A400001, 0x34800001, 0x69000001, 0xD2000001, 
        0xA4000001, 0x48000001, 0x90000001, 0x20000001, 0x40000001, 0x80000001, 0x00000001, 0x00000001)
        
    ADD = (
        0x69C77F93, 0x3DAA512A, 0x8CDD2764, 0x5F040108, 0xFAE49B10, 0xCF081A20, 0xCD4FC440, 0xA7BDC880, 
        0xE4F49100, 0x27CD2200, 0x072A4400, 0xEC948800, 0x52291000, 0x88522000, 0xA0A44000, 0x81488000, 
        0x02910000, 0x05220000, 0x0A440000, 0x14880000, 0x29100000, 0x52200000, 0xA4400000, 0x48800000, 
        0x91000000, 0x22000000, 0x44000000, 0x88000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000)

class BWRNG(LCRNG):
    MASK = 0xFFFFFFFFFFFFFFFF
    BITS = 64

    MUL = (
        0x5D588B656C078965, 0x722C73D8054341D9, 0x355BC66E0285E9F1, 0x6C5234D0AE3294E1, 0x4D5A22005A78EDC1, 0x84D4844B75BEEB81, 0x2C8B173C56221701, 0xF02DE276CA552E01, 
        0x9804B5DD28EE5C01, 0xD0379E6982ECB801, 0x8CB37296CA197001, 0xD6824C74A532E001, 0x82BA37C58E65C001, 0x35C2F8FC2CCB8001, 0xEC0087BC99970001, 0x0BEEE68A332E0001, 
        0xF7B12958665C0001, 0xEF8FC3C0CCB80001, 0xE6D54BC199700001, 0x2481A88332E00001, 0x645F950665C00001, 0x36303A0CCB800001, 0x2224B41997000001, 0x1B5A68332E000001, 
        0x92F8D0665C000001, 0x9701A0CCB8000001, 0xF243419970000001, 0xF5868332E0000001, 0x2F0D0665C0000001, 0x6E1A0CCB80000001, 0x1C34199700000001, 0x3868332E00000001, 
        0x70D0665C00000001, 0xE1A0CCB800000001, 0xC341997000000001, 0x868332E000000001, 0x0D0665C000000001, 0x1A0CCB8000000001, 0x3419970000000001, 0x68332E0000000001, 
        0xD0665C0000000001, 0xA0CCB80000000001, 0x4199700000000001, 0x8332E00000000001, 0x0665C00000000001, 0x0CCB800000000001, 0x1997000000000001, 0x332E000000000001, 
        0x665C000000000001, 0xCCB8000000000001, 0x9970000000000001, 0x32E0000000000001, 0x65C0000000000001, 0xCB80000000000001, 0x9700000000000001, 0x2E00000000000001,
        0x5C00000000000001, 0xB800000000000001, 0x7000000000000001, 0xE000000000000001, 0xC000000000000001, 0x8000000000000001, 0x0000000000000001, 0x0000000000000001)

    ADD = (
        0x0000000000269EC3, 0x7188D00C55AE9CB2, 0x0A8B4E34C910A194, 0x229675654EAC71E8, 0x9D8474851566AED0, 0x0E7F4341592709A0, 0xAF8278456068C340, 0x6545AEB598DC4680, 
        0xED1F0EA72EE38D00, 0x536510BD3A731A00, 0x6A3422CD27963400, 0x5C11E19F19EC6800, 0xB85689215ED8D000, 0xA5D4D84F69B1A000, 0x42CE3CD183634000, 0x705A4A6DC6C68000, 
        0x9D08D8068D8D0000, 0xB64ABCB91B1A0000, 0xB4B9AC2236340000, 0x440423046C680000, 0xC24B7108D8D00000, 0xEDA38E11B1A00000, 0x7F79CC2363400000, 0x8FBE5846C6800000, 
        0x62A7B08D8D000000, 0xD1FB611B1A000000, 0xD6A6C23634000000, 0x780D846C68000000, 0x1B1B08D8D0000000, 0xE23611B1A0000000, 0x746C236340000000, 0xA8D846C680000000, 
        0x51B08D8D00000000, 0xA3611B1A00000000, 0x46C2363400000000, 0x8D846C6800000000, 0x1B08D8D000000000, 0x3611B1A000000000, 0x6C23634000000000, 0xD846C68000000000, 
        0xB08D8D0000000000, 0x611B1A0000000000, 0xC236340000000000, 0x846C680000000000, 0x08D8D00000000000, 0x11B1A00000000000, 0x2363400000000000, 0x46C6800000000000, 
        0x8D8D000000000000, 0x1B1A000000000000, 0x3634000000000000, 0x6C68000000000000, 0xD8D0000000000000, 0xB1A0000000000000, 0x6340000000000000, 0xC680000000000000,
        0x8D00000000000000, 0x1A00000000000000, 0x3400000000000000, 0x6800000000000000, 0xD000000000000000, 0xA000000000000000, 0x4000000000000000, 0x8000000000000000)
    
    def rand(self, lim=0):
        rnd = self.next() >> 32
        return (rnd * lim) >> 32 if lim else rnd >> 16
    
class BWRNGR(BWRNG):
    MUL = (
        0xDEDCEDAE9638806D, 0xF216A9242C1D2E69, 0x7521BACFA433E711, 0x7D68EC11A955AF21, 0x6D18584955B82241, 0x5D7404426C055481, 0x59E019ED40EEE901, 0x6815F15091EED201, 
        0x74038B504821A401, 0x7178874C41534801, 0x12FF344046E69001, 0x37694EE79ECD2001, 0xA70435AB819A4001, 0x9236BCC813348001, 0x43E64F5466690001, 0xB3AC75B9CCD20001, 
        0x06BC47B799A40001, 0x0A26007F33480001, 0x0001C53E66900001, 0x76DA9B7CCD200001, 0x09117AF99A400001, 0x7F9405F334800001, 0xB4EC4BE669000001, 0x40E997CCD2000001, 
        0xDE172F99A4000001, 0x2D3E5F3348000001, 0x1EBCBE6690000001, 0x4E797CCD20000001, 0xE0F2F99A40000001, 0xD1E5F33480000001, 0xE3CBE66900000001, 0xC797CCD200000001, 
        0x8F2F99A400000001, 0x1E5F334800000001, 0x3CBE669000000001, 0x797CCD2000000001, 0xF2F99A4000000001, 0xE5F3348000000001, 0xCBE6690000000001, 0x97CCD20000000001, 
        0x2F99A40000000001, 0x5F33480000000001, 0xBE66900000000001, 0x7CCD200000000001, 0xF99A400000000001, 0xF334800000000001, 0xE669000000000001, 0xCCD2000000000001, 
        0x99A4000000000001, 0x3348000000000001, 0x6690000000000001, 0xCD20000000000001, 0x9A40000000000001, 0x3480000000000001, 0x6900000000000001, 0xD200000000000001,
        0xA400000000000001, 0x4800000000000001, 0x9000000000000001, 0x2000000000000001, 0x4000000000000001, 0x8000000000000001, 0x0000000000000001, 0x0000000000000001)

    ADD = (
        0x9B1AE6E9A384E6F9, 0x1C1530CD230FBEFE, 0x11EF4891A39CB92C, 0x1412364CFFDFB918, 0x2042EA353835FD30, 0xF93379BE940BA660, 0xD45E8E85C061FCC0, 0x3D4BF12DAA4EB980, 
        0x6915BC51DDC87300, 0x89D2D1E6F83CE600, 0xB0F6D3C3A329CC00, 0x7550B8A411139800, 0xD89FDFEB4D273000, 0x54C4CBE3464E6000, 0x139853F93C9CC000, 0xA93FF8BD39398000, 
        0xC96034A572730000, 0xE35975F6E4E60000, 0xB1D71E9DC9CC0000, 0x563F07FB93980000, 0xA6C13AF727300000, 0xB68F21EE4E600000, 0x1150F3DC9CC00000, 0xB36CA7B939800000, 
        0xAA044F7273000000, 0x60B49EE4E6000000, 0xF4193DC9CC000000, 0xB2F27B9398000000, 0x90E4F72730000000, 0xCDC9EE4E60000000, 0x4B93DC9CC0000000, 0x5727B93980000000, 
        0xAE4F727300000000, 0x5C9EE4E600000000, 0xB93DC9CC00000000, 0x727B939800000000, 0xE4F7273000000000, 0xC9EE4E6000000000, 0x93DC9CC000000000, 0x27B9398000000000, 
        0x4F72730000000000, 0x9EE4E60000000000, 0x3DC9CC0000000000, 0x7B93980000000000, 0xF727300000000000, 0xEE4E600000000000, 0xDC9CC00000000000, 0xB939800000000000, 
        0x7273000000000000, 0xE4E6000000000000, 0xC9CC000000000000, 0x9398000000000000, 0x2730000000000000, 0x4E60000000000000, 0x9CC0000000000000, 0x3980000000000000,
        0x7300000000000000, 0xE600000000000000, 0xCC00000000000000, 0x9800000000000000, 0x3000000000000000, 0x6000000000000000, 0xC000000000000000, 0x8000000000000000)