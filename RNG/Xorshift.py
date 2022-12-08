import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util.Bits import reverse_xor_lshift_mask, reverse_xor_rshift_mask

class Xorshift:
    def __init__(self, s0, s1=None, state=None):
        if state is not None:
            self._state = state.copy()
        elif s1 is None:
            self._state = [0] * 4
            
            self._state[0] = s0 & 0xffffffff
            for i in range(1, 4):
                self._state[i] = (self._state[i-1] * 0x6c078965 + 1) & 0xffffffff
        else:                               
            self._state = [s0 >> 32, s0 & 0xffffffff, s1 >> 32, s1 & 0xffffffff]
    
    @property
    def state(self):
        return (self._state[0] << 96) | (self._state[1] << 64) | (self._state[2] << 32) | self._state[3]
    
    @property
    def states(self):
        s0 = (self._state[0] << 32) | self._state[1]
        s1 = (self._state[2] << 32) | self._state[3]
        return (s0, s1)
    
    def next(self):
        t = self._state[0]
        t ^= (t << 11) & 0xffffffff
        t ^= (t >> 8) ^ self._state[3] ^ (self._state[3] >> 19) 
 
        self._state[0] = self._state[1]
        self._state[1] = self._state[2]
        self._state[2] = self._state[3]
        self._state[3] = t

        return t
    
    def prev(self):
        t = self._state[3] ^ self._state[2] ^ (self._state[2] >> 19) 
        t = reverse_xor_rshift_mask(t, 8)
        t = reverse_xor_lshift_mask(t, 11)

        self._state[3] = self._state[2]
        self._state[2] = self._state[1]
        self._state[1] = self._state[0]
        self._state[0] = t

        return self._state[3]

    def next_u32(self):
        return (self.next() % 0xffffffff) ^ 0x80000000
    
    def rand(self, lim):
        return self.next_u32() % lim

    def jump_ahead(self, n):
        i = 0
        
        while n and i < 128:
            if n & 1:
                jump = XORSHIFT_JUMP_TABLE[i]
                s0 = s1 = s2 = s3 = 0

                while jump:
                    if jump & 1:
                        s0 ^= self._state[0]
                        s1 ^= self._state[1]
                        s2 ^= self._state[2]
                        s3 ^= self._state[3]

                    self._next_state()
                    jump >>= 1
                
                self._state = [s0, s1, s2, s3]
            
            n >>= 1
            i += 1

    def advance(self, n=1):
        for _ in range(n):
            self.next()
    
    def back(self, n=1):
        for _ in range(n):
            self.prev()
            
    # Ignoring the case of multiple solutions (2^n solutions with n the number of occurence of 0x80000000 in the outputs, 0x7fffffff output is impossible)
    @staticmethod
    def recover_states_from_4_32bit_outputs(out1, out2, out3, out4): 
        s0 = ((out1 << 32) | out2) ^ 0x8000000080000000
        s1 = ((out3 << 32) | out4) ^ 0x8000000080000000
        
        x = Xorshift(s0, s1)
        x.back(4)

        return x.states

XORSHIFT_JUMP_TABLE = (
    0x00000000000000000000000000000002, 0x00000000000000000000000000000004, 0x00000000000000000000000000000010, 0x00000000000000000000000000000100, 
    0x00000000000000000000000000010000, 0x00000000000000000000000100000000, 0x00000000000000010000000000000000, 0x000000010046D8B3F985D65FFD3C8001, 
    0x956C89FBFA6B67E9A42CA9AEB1E10DA6, 0xFF7AA97C47EC17C71A0988E988F8A56E, 0x9DFF33679BD01948FB6668FF443B16F0, 0xBD36A1D3E3B212DA46A4759B1DC83CE2, 
    0x6D2F354B8B0E3C0B9640BC4CA0CBAA6C, 0xECF6383DCA4F108F947096C72B4D52FB, 0xE1054E817177890A0DAF32F04DDCA12E, 0x02AE1912115107C6B9FA05AAB78641A5, 
    0x59981D3DF81649BE382FA5AA95F950E3, 0x6644B35F0F8CEE00DBA31D29FC044FDB, 0xECFF213C169FD4553CA16B953C338C19, 0xA9DFD9FB0A0949393FFDCB096A60ECBE, 
    0x079D7462B16C479FFD6AEF50F8C0B5FA, 0x03896736D707B6B69148889B8269B55D, 0xDEA22E8899DBBEAA4C6AC659B91EF36A, 0xC1150DDD5AE7D32067CCF586CDDB0649, 
    0x5F0BE91AC7E9C38133C8177D6B2CC0F0, 0x0CD15D2BA212E5734A5F78FC104E47B9, 0xAB586674147DEC3ED69063E6E8A0B936, 0x4BFD9D67ED3728667071114AF22D34F5, 
    0xDAF387CAB4EF5C18686287302B5CD38C, 0xFFAF82745790AF3EBB7D371F547CCA1E, 0x7B932849FE573AFAEB96ACD6C88829F9, 0x8CEDF8DFE2D6E821B4FD2C6573BF7047, 
    0xB067CC93D37390513532E5F33A883107, 0xFE1A817D36419BAA9682C4C3023090E7, 0xAFDCBF8B4555ED5FAE6D35E0269DB445, 0xCD0DC146540609A174A47EC949A2536B, 
    0xF0BF2D2CDC59EBB01809F899E9E69F80, 0x6F82DDB5ABC7D64D15F1121FEFB4F4DC, 0xDC0B508281574220E6CBA91144CBBBE6, 0xB04BED1CD5BA396EA2C0A5A1D95AEB31, 
    0x862F99D765FCB394CCB635F89186D420, 0xDBB253DADE5AAE15A5B598875BFAEF90, 0x14136DE0A527D5F106F04C1D1F94AA7C, 0xB9ACC1C3A2E84C2EC06B983CDC17108B, 
    0x286C710524D0B048795D42886E61C7B7, 0x969493371D04723885658FA74F66EF2B, 0x228DC4710D53FBC84E89AF13D636BEFB, 0x0CCEB170A295DA669D022830D50DF99D, 
    0xDDC435583E0A2DA1F88C1CF697E0579A, 0xB3360EC1CB3043DA6EBD25B376ED1362, 0x665D04AD04E9DD37A6486F63EBCF8D60, 0xA9FDD1C73437FB2A11DA01041533B855, 
    0x12659E0E814A99258AECE6B835A3A0F0, 0xBC2B6ECD67109D0974DD61DB2CD1F179, 0x5596F764B9F024C6A3382FADBC64A64E, 0x2E619BBD5C61C40F36B3D3A34A3A51EB, 
    0xAD17C26FF61DDB9AF9220668547D1FB2, 0x8768B12BD95D4A24BA45341289F8CF2D, 0xDA050F7D87B5D735660B2988413894B1, 0x98D18BF7C6FC9C795577ABCE14157C23, 
    0xBA46C07CCBFA874B95EA3AB49A46F6DC, 0xB3F66A175D848E85449DA58268DBBB93, 0x29CB68289069C270F973F85EBC0EE1BE, 0xC5D522132349BF61EA3BCF8EE7DEFF39, 
    0xD8CD644EF52E65C4821E534335AAC71C, 0x06D992569A61A161D2C1ECEF023E487B, 0x29C23F71037ECB6F04193A0C13B7FF17, 0xDD86DBB37C7393B34AB914F1CC67A971, 
    0x4F8C624E45559BE0D85688F4EA5F6513, 0x3682F88E03CD644A28E99D0CC6A2C63C, 0x1A7632F601A7630B27690A8FDB447239, 0x208E7B1A72BD44E68587B2073D9487B4, 
    0x7B01DEB53BFD70D1022E8DE3F4D585A8, 0xE4B29364C9B2EC7CE3B7DDB95FA88846, 0x0F51758987EC6F749145059C01FC548D, 0x303C817CB27551DF4DDB8CA5D40C20C2, 
    0xE9F1697FDA14DDD3E795D59D4D1343EF, 0xB9EEEC6B433DC852B60B5D2BECBBDFD3, 0x6BB3B410CAAA66DEEDDC01A55C6CAF41, 0xE44B795191C21CEF6FD25C2FCCC4C92C, 
    0x9B306B19F81CE25CFE113B9AAC588C17, 0xC5F9B7800BE81E29539CEE04B38FBEFC, 0x1E5C87EF4ABB97807E70AA88BCFF3655, 0x76633CB7DA0DF635E2B030D25D458961,
    0x662921BA0CCAD483BFF754CEC95D5FF3, 0xA56529B955637BE63B1D7328EB3EF2E8, 0x631231BAF441CFD7CADE09B55BBC21E5, 0x8EA70BD1786FAB7DFFAA419D769CF298,
    0x810881EE0B2BCDBE22B7F6AEDB26A041, 0x27E1D81B54E6B7EDCDE2B549D2A36B50, 0xF8F97377345656238FEA4223882C8963, 0x1BC3E4E6BA6A1F16936349E37C20A404,
    0x6F01D7F36B187C991E5293C0880E89C7, 0xB60F1C3028A32AE4F1DDC55A8B46D420, 0x90E457646AE8C38D8E3CAD40086D105E, 0xE85346EABF5120726F3BA07AC555249B,
    0x32E5CF7230FF27CBCF407DCC3FE5F618, 0x118012EF704B515F9C869A9ED1CDCDB5, 0xDC3ED9F394C1EF63317D4E063E956D2B, 0xC489C7F3A2D968B82CB2BD2156EC0D3C,
    0xA6DE0F9AA3FA48365F740A6C803E5A4A, 0xB584748D4624BC113CF8318C8498F41C, 0x48B1A2A8F4EAF2B383829B068C970A74, 0xC4417E2AD0EAEA052CBDC7F4C2AC7C91,
    0x0C675FB0976B1595C4C8BC1ED88650B7, 0x04DCCD187067DD8990B8FCB34A1EEB79, 0xEEDF835055E9742E482269DAEA523CF8, 0xAC11BF4793485EC2728BD207BAA40D16,
    0xEDA4600D68F7E41E049B2E897CB3015B, 0xDFEF2A85CE12C0228FFBE1C00FE85999, 0x4A46A25E3DE228F560F71A4753EBBCF6, 0x6C54373E5A67F34F002D52F95FCF8D67,
    0xBA57F82A1D29D4262E516844721503F0, 0x721DB46E483C68027F8B0DA24E87E946, 0x89B0625303C74F0B118C55636C7B0BA7, 0xBADD34856E872354E1998F3494B875BD,
    0x68C3AFDD3BA4C42D850702CEECAD8500, 0xF36FDE34B48FBBA426E4433AA692C9D5, 0x539FDC541BB3FC038BC1482FF3783BCC, 0xBB00FA4EBEC0F6B538B5FFCC66884AE6,
    0xEBCF83D233A66F96A46944F11F2B2FC8, 0xF7D46C3248FC046192A9DB106CD5D704, 0x18C8C81B338708F78DA3E03E43B215DD, 0xBA28BA9CF175EA1C00E3E1A37AC657F6,
    0x3DE53FA1E9B03CAFD0A5F82F1E00DF0B, 0xE112AED18898D49A7B4C0943015B33DF, 0xD9E63EC817BF84E121702C522010C0E0, 0x4D59E5D1E22DB1BFA86B1B09FE3FDBF4)

if __name__ == "__main__":
    from random import randrange

    lim = 1 << 64

    '''s0 = randrange(0, lim)
    s1 = randrange(0, lim)

    print(hex(s0), hex(s1))

    rng = Xorshift(s0, s1)
    for i in range(10):
        print(i, hex(rng.next()))'''

    '''s0 = randrange(0, lim)
    s1 = randrange(0, lim)
    a = 12_345_678

    rng1 = Xorshift(s0, s1)
    rng1.advance(a)
    print(hex(rng1.state))

    rng2 = Xorshift(s0, s1)
    rng2.jump_ahead(a)
    print(hex(rng2.state))'''

    s0, s1 = Xorshift.recover_states_from_4_32bit_outputs(0xdeadbeef, 0xaaaaaaaa, 0xc0cac01a, 0x12345678)    
    print(hex(s0), hex(s1))

    rng = Xorshift(s0, s1)
    for _ in range(4):
        print(hex(rng.next_u32())) 