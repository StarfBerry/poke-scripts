import os, sys
path = os.path.dirname(__file__)
sys.path.append(path)
sys.path.append(path + "\..")

from Util.Bits import reverse_lshift_xor_mask, reverse_rshift_xor_mask
from Matrix_GF2.GF2 import gf2_to_int, gf2_to_ints, tinymt_jump_poly

class TinyMT:    
    A = 0x8F7011EE
    B = 0xFC78FF1F
    C = 0x3793FDFF
    M = 0x6C078965

    def __init__(self, seed=0, state=None):
        if state is not None:
            self._state = state.copy()
            self._period_certification()
        else:
            self._state = [seed & 0xffffffff, TinyMT.A, TinyMT.B, TinyMT.C]
            for i in range(1, 8):
                self._state[i & 3] ^= (TinyMT.M * (self.state[(i - 1) & 3] ^ (self.state[(i - 1) & 3] >> 30)) + i) & 0xffffffff
                                                                                                                   
            self._period_certification()
            self.advance(8)
    
    @property
    def state(self):
        return self._state.copy()

    def next(self):
        self._next_state()
        return self._temper()
    
    def prev(self):
        self._prev_state()
        return self._temper()

    def jump_ahead(self, n):
        jump = tinymt_jump_poly(n)
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

    def advance(self, n=1):
        for _ in range(n):
            self._next_state()
    
    def back(self, n=1):
        for _ in range(n):
            self._prev_state()
    
    def rand(self, lim):
        return (self.next() * lim) >> 32
    
    def prev_rand(self):
        return (self.prev() * lim) >> 32
    
    def _next_state(self):
        x = (self._state[0] & 0x7fffffff) ^ self._state[1] ^ self._state[2]
        y = self._state[3]

        x ^= (x << 1) & 0xffffffff
        y ^= (y >> 1) ^ x

        self._state[0] = self._state[1]
        self._state[1] = self._state[2]
        self._state[2] = x ^ (y << 10) & 0xffffffff
        self._state[3] = y

        if y & 1:
            self._state[1] ^= TinyMT.A
            self._state[2] ^= TinyMT.B
            
    def _prev_state(self):
        y = self._state[3]
        x = self._state[2] ^ (y << 10) & 0xffffffff

        self._state[2] = self._state[1]
        self._state[1] = self._state[0]

        if y & 1:
            self._state[2] ^= TinyMT.A
            x ^= TinyMT.B

        y = reverse_rshift_xor_mask(y ^ x)
        x = reverse_lshift_xor_mask(x)

        self._state[3] = y
        self._state[0] = x ^ self._state[1] ^ self._state[2]
        
        x_ = (self._state[2] ^ (y << 10) ^ (y & 1) * TinyMT.B) & 0xffffffff
        xor = (self._state[1] >> 31) ^ (y & 1) ^ (x_ >> 31) ^ (reverse_lshift_xor_mask(x_) >> 30) & 1

        if xor:
            self._state[0] ^= 0x80000000

    def _temper(self):
        t = (self._state[0] + (self._state[2] >> 8)) & 0xffffffff
        return self._state[3] ^ t ^ (t & 1) * TinyMT.C
    
    def _period_certification(self):
        if self._state[0] & 0x7fffffff == 0 and self._state[1] == 0 and self._state[2] == 0 and self._state[3] == 0:
            self._state = [ord('T'), ord('I'), ord('N'), ord('Y')]
    
    def __repr__(self):
        return f"S[0]: {self._state[0]:08X}\nS[1]: {self._state[1]:08X}\nS[2]: {self._state[2]:08X}\nS[3]: {self._state[3]:08X}"

    @staticmethod
    def reverse_init_loop(s):
        for i in range(7, 0, -1):
            s[i & 3] ^= (TinyMT.M * (s[(i- 1) & 3] ^ (s[(i - 1) & 3] >> 30)) + i) & 0xffffffff

    @staticmethod
    def recover_seed_from_state(state, min_advc=0, max_advc=10_000):
        rng = TinyMT(state=state)
        rng.back(8 + min_advc) # advances of 8 in the constructor
        advc = max_advc - min_advc

        for _ in range(advc + 1):
            s = rng.state
            TinyMT.reverse_init_loop(s)
            
            if s[3] == TinyMT.C:
                if s[1] == TinyMT.A and s[2] == TinyMT.B:
                    return s[0]
                
                c = rng.state
                c[0] ^= 0x80000000
                TinyMT.reverse_init_loop(c)
                
                if c[1] == TinyMT.A and c[2] == TinyMT.B:
                    return c[0]
            
            rng.back()
        
        return -1
    
    @staticmethod
    def recover_state_from_127_lsb(bits):
        if len(bits) != 127:
            raise ValueError("127 bits are needed to recover the internal state.")

        vec = gf2_to_int(bits)
        
        for i in range(127):
            bits[i] = (vec & MAT_TINYMT_127_LSB_INV[i]).bit_count() & 1
        
        bits.insert(31, 0)
        
        return gf2_to_ints(bits, 32)

    @staticmethod
    def recover_seed_from_127_lsb(bits, min_advc=0, max_advc=10_000):
        state = TinyMT.recover_state_from_127_lsb(bits)
        state = TinyMT.advance_state(state)
        return TinyMT.recover_seed_from_state(state, min_advc+1, max_advc+1)

    @staticmethod
    def advance_state(state, n=1):
        rng = TinyMT(state=state)
        rng.advance(n)
        return rng.state

    @staticmethod
    def backward_state(state, n=1):
        rng = TinyMT(state=state)
        rng.back(n)
        return rng.state

MAT_TINYMT_127_LSB_INV = (
    0x5FC1AAB2E39C4434AF630C9B9374B832, 0x1085296E28C0425ABD3BDA1869A675F1, 0x31C7020BDEBC413D2C23BA331C3BE6FC, 0x224AEB96ADD3739269E216E9BBD26EC9, 
    0x2A335AD5F6E13D067E22D643E79CD92E, 0x2EC75958BA057AD8DEB7E9E63117D9AB, 0x2CD358B8CFE73970E769C722C8A18CB0, 0x2DEB94943D604BB253582C1F25385E43, 
    0x2D6C077E2A7A2373347150FC3CB5F0FE, 0x2D2343FDB9BAB82A02FF951D9B993151, 0x5D237E3D6F7DCB492F551181AE422688, 0x30C48335335FEB7FDECC07E80CC01041, 
    0x4B79F55CC2563B50A925A653684A5D01, 0x668CDA849CD2E78C16F3746C77F1BD4D, 0x40160FF7C6DB891D1E6349B08F0545C8, 0x32F3516717ECA59FFA7967F7689DD586, 
    0x7DA1B0D3E68B56C34A3130D70705F98C, 0x026822282FAD804BA827F3266CCF66A6, 0x71441643F3F1F14EEC6D5D890574B761, 0x4C66DA6DF0F8D52D90C1691508849DD0, 
    0x68D2E0330E2D5AB6342643143AFBB98C, 0x3869A1AD6FF21DBD18913AE950077189, 0x3D18DB386EE006904314746FD0E3D31C, 0x0AB10C8B50A4DEE18B313D3B9506DFBF, 
    0x15223BA0BFA7AF5FD26ADC5840EA9CA6, 0x4565CEF9CF39E9A95B1D11B300831BD9, 0x4237CE9AA242A7365675B6334942AFE4, 0x2E35B759CB0A7AF50B6373C3E47CC7F7, 
    0x304DBF0B31290B888128290B400B43A1, 0x357CE0F104B37FABF4E3ED4C8F5BEDDC, 0x36B366315D351E0749DC908D9BA36CA6, 0x67D115472AB57723D30A49F0BE13CA27, 
    0x210A52DC518084B57A77B430D34CEBE2, 0x638E0417BD78827A584774663877CDF8, 0x4495D72D5BA6E724D3C42DD377A4DD92, 0x5466B5ABEDC27A0CFC45AC87CF39B25C, 
    0x5D8EB2B1740AF5B1BD6FD3CC622FB356, 0x59A6B1719FCE72E1CED38E4591431960, 0x5BD729287AC09764A6B0583E4A70BC86, 0x5AD80EFC54F446E668E2A1F8796BE1FC, 
    0x5A4687FB7375705405FF2A3B373262A2, 0x6214BC58337669D8D36673C4C47EF753, 0x6189066A66BFD6FFBD980FD019802082, 0x4EA1AA9B692189EBDF871C61486E0041, 
    0x154BF52BD4283052A02AB81F7719C0D9, 0x587E5FCD603AED70B10AC3A686F031D3, 0x65E6A2CE2FD94B3FF4F2CFEED13BAB0C, 0x23112185209B52CC19AE316996F1495B, 
    0x04D044505F5B0097504FE64CD99ECD4C, 0x3ADA6CA50A6E1DD75516EBD59213D481, 0x409FF4F90C7C5511AC4E82ED89F381E3, 0x09F78044F1D74A26E580D6EFED0DC95B, 
    0x70D3435ADFE43B7A312275D2A00EE312, 0x7A31B670DDC00D208628E8DFA1C7A638, 0x15621916A149BDC316627A772A0DBF7E, 0x2A4477417F4F5EBFA4D5B8B081D5394C, 
    0x5299DDD173FE2C183BF673A199FC8DF1, 0x5C3DDD17A908B12621273CA10A7FE58B, 0x5C6B6EB39614F5EA16C6E787C8F98FEE, 0x609B7E16625217110250521680168742, 
    0x6AF9C1E20966FF57E9C7DA991EB7DBB8, 0x6D66CC62BA6A3C0E93B9211B3746D94C, 0x29C784A6A5568164503ADBF47515BD8E, 0x17F06AACB8E7110D2BD8C326E4DD2E0D,
    0x4214A5B8A301096AF4EF6861A699D7C6, 0x1F4E480D977CFBBE3D42B80BE81521B1, 0x5179EE785AC031032A440B6177B30165, 0x709F2B7536090B53754709C80689DEFB,
    0x634F254005981429F713F75F5CA5DCED, 0x6B1F22C1D2111A89106B4C4CBA7C8881, 0x6FFC1272180CD183C0ACE0BB0C1BC34D, 0x6DE25DDA446572865C0913376A2D79B9,
    0x6CDF4FD40B671FE2863204B1F69E7F07, 0x1C7B38928B612CFB2B00B74E100754E5, 0x1B404CF620F252B5F6FC4F67ABFAFB47, 0x451115143FCEEC9D32C268050826BAC3,
    0x2A97EA57A85060A54055703EEE3381B2, 0x68AEFFB82DF825ABEFD9D78A951AD9E5, 0x139F05BEB23F69356429CF1A3A8DEC5B, 0x4622430A4136A598335C62D32DE292B6,
    0x09A088A0BEB6012EA09FCC99B33D9A98, 0x75B4D94A14DC3BAEAA2DD7AB2427A902, 0x596DA9D0F5755569D551551C8B1DB985, 0x13EF0089E3AE944DCB01ADDFDA1B92B4,
    0x39F4C697524589BEEF88BB62D8E77C65, 0x2C312CC3560DE50B819D8178DB75F631, 0x2AC4322D42937B862CC4F4EE541B7EFC, 0x5488EE82FE9EBD7F49AB716103AA729A,
    0x7D61FB800A71A77AFA20B784AB03A1A3, 0x6029FA0DBF9C9D06CF8229858C057157, 0x60849D45C1A4149EA0419FC80909A59D, 0x1964BC0E2929D168896CF4EA98D7B4C7,
    0x0DA1C3E6FF4001E55E43E5F5A5950D33, 0x029FD8E799598757AABE12F1F67708DB, 0x538F094D4AAD02C8A075B7E8EA2B7B1E, 0x00000000000000000000000000000001,
    0x2FE0D55971CE221A57B1864DC9BA5C1B, 0x2C5A74B839DD8BB19CC00AD28F07F1E0, 0x4A720DD3649F6BAEDFC56F6041225140, 0x7C65CA851821DEF534C7A7622C00F108,
    0x65900965447075B9B7C6FA367912AEEC, 0x682E512FC7A0B699366CE0E4327C4AEE, 0x6E4CB6F3ECC3EEB97A63B9B5227DCE30, 0x6D2DFFF0055D90CC0FFD0BA97EB1D4CA,
    0x6CB2BBA4872C5458A8153A9557888E2E, 0x6C6953459FBAC32CF45B46DC15A56C7E, 0x541FC4C95B80E3C9C720F53F861BA70B, 0x4D333E27A3743A4F8636DDD3D6571DE4,
    0x05C38130E9BA8089D65FA3DB74BBB068, 0x17DD0C7A4EDC68C7C80C8A175B15CB1D, 0x11F17EF4B8D74FF5EE297FE89F0A0CFF, 0x065FDA88C86A164D1869BAA6BEDA2A2E,
    0x56F84BD255921CD522DBCB85FC53CEC2, 0x34D0A0D05A5DFA50D294B6D72674FA16, 0x6C43AC04CDE558343C1C637DDFB1F5AA, 0x072890C75F10157433602A524102CBE9,
    0x2E2756F3F4956E14A6D9F836C4801BEE, 0x71EDBF8AE3B8999937F6C426688320AF, 0x5032E556CE3A1423574DF53CA3C0B659, 0x760A09E2E9903530812CE1E83DFAFD80,
    0x1CB5DFD65A35F420803AD4D4F770758E, 0x24AD2AB1669E32352590BD62E9797E69, 0x79497EFBA9C2BF824CAAB126C6CF8E08, 0x3F706E013FA62F5B5D072B37391EFEE7,
    0x1AF88BBFA602279D50F9F92236659E89, 0x349F032662C1244FB87956B1361DE8E8, 0x56CF952B2BD04897FB378A9434CDBF5E)

if __name__ == "__main__":
    from random import randrange

    '''seed = randrange(0, 1 << 32)
    rng = TinyMT(seed)
    it = 10_000

    a = [rng.next() for _ in range(it)]
    rng.next()

    b = [rng.prev() for _ in range(it)]
    b.reverse()

    print(a == b)'''

    '''seed = randrange(0, 1 << 32)
    rng = TinyMT(seed)
    it = 10_000

    a = []
    for _ in range(it):
        a.append(rng.state)
        rng.next()
    
    b = []
    for _ in range(it):
        rng.prev()
        b.append(rng.state)
    
    b.reverse()
    
    print(a == b)'''

    '''s = randrange(0, 1 << 32)
    a = randrange(0, 10000)
    
    tinymt = TinyMT(s)
    tinymt.advance(a)
    
    r = TinyMT.recover_seed_from_state(tinymt.state)
    
    print(f"Recovered Seed: {r:08X} | Expected Seed: {s:08X} | Advances: {a}")'''

    '''seed = randrange(0, 1 << 32)
    rng = TinyMT(seed)

    a = rng.state

    rng.jump_ahead((1 << 127) - 17)
    rng.advance(16)

    b = rng.state

    print(a == b)
    '''        

    '''for _ in range(10_000):
        seed = randrange(0, 1 << 32)
        a = randrange(0, 100)

        rng = TinyMT(seed)
        rng.advance(a)

        bits = [rng.next() & 1 for _ in range(127)]

        test = TinyMT.recover_seed_from_127_lsb(bits, max_advc=100)
        
        if seed != test:
            print(hex(seed))'''

    '''seed = randrange(0, 1 << 32)
    a = 12_345_678

    rng1 = TinyMT(seed)
    rng1.advance(a)

    rng2 = TinyMT(seed)
    rng2.jump_ahead(a)

    print(rng2)
    print()
    print(rng2)'''

    seed = randrange(0, 1 << 32)
    rng = TinyMT(seed)
    rng.advance(randrange(0, 100))

    state = TinyMT.advance_state(rng.state)
    state[0] &= 0x7FFFFFFF

    bits = [rng.next() & 1 for _ in range(127)]
    
    test = TinyMT.recover_state_from_127_lsb(bits)

    for i in range(4):
        print(f"{state[i]:08X} {test[i]:08X}")