import sys
sys.path.append(".")
sys.path.append("../")

from Util import reverse_lshift_xor_mask
from RNG import MT 

class SFMT:
    A = 0
    B = 488
    C = 616
    D = 620
    N = 624
    
    MASK = 0xFFFFFFFF
    MSK1 = 0xDFFFFFEF
    MSK2 = 0xDDFECB7F
    MSK3 = 0xBFFAFFFF
    MSK4 = 0xBFFFFFF6
    
    PARITY = [0x1, 0x0, 0x0, 0x13C9E684]
    
    def __init__(self, seed, bits64=True):
        self._state = [0] * SFMT.N

        self._state[0] = seed
        for i in range(1, SFMT.N):
            self._state[i] = (0x6C078965 * (self._state[i-1] ^ (self._state[i-1] >> 30)) + i) & SFMT.MASK
        
        self._period_certification()
        self._twist()
        self._index = 0
        
        self.next = self._next64 if bits64 else self._next32
    
    @property
    def state(self):
        return self._state.copy()

    def advance(self, n=1):
        self._index += n

        if self._index >= SFMT.N:
            q, self._index = divmod(self._index, SFMT.N)
            for _ in range(q): 
                self._twist()

    def _next32(self):
        if self._index == self.N:
            self._twist()
            self._index = 0

        n = self._state[self._index]
        self._index += 1

        return n
    
    def _next64(self):
        if self._index == self.N:
            self._twist()
            self._index = 0

        low = self._state[self._index]
        high = self._state[self._index + 1]
        self._index += 2

        return (high << 32) | low
    
    def _period_certification(self):
        inner = 0

        for i in range(4):
            inner ^= self._state[i] & SFMT.PARITY[i]
        
        i = 16
        while i > 0:
            inner ^= inner >> i
            i >>= 1
        
        if inner & 1:
            return
        
        for i in range(4):
            work = 1
            for _ in range(32):
                if work & SFMT.PARITY[i]:
                    self._state[i] ^= work
                    return
                work <<= 1

    
    def _twist(self):
        a, b, c, d = SFMT.A, SFMT.B, SFMT.C, SFMT.D

        while a < 624:
            self._state[a+3] ^= (self._state[a+3] << 8) & SFMT.MASK
            self._state[a+3] ^= self._state[a+2] >> 24
            self._state[a+3] ^= self._state[c+3] >> 8
            self._state[a+3] ^= (self._state[b+3] >> 11) & SFMT.MSK4
            self._state[a+3] ^= (self._state[d+3] << 18) & SFMT.MASK
            
            self._state[a+2] ^= (self._state[a+2] << 8) & SFMT.MASK
            self._state[a+2] ^= self._state[a+1] >> 24
            self._state[a+2] ^= self._state[c+2] >> 8
            self._state[a+2] ^= (self._state[b+2] >> 11) & SFMT.MSK3
            self._state[a+2] ^= (self._state[c+3] << 24) & SFMT.MASK
            self._state[a+2] ^= (self._state[d+2] << 18) & SFMT.MASK
            
            self._state[a+1] ^= (self._state[a+1] << 8) & SFMT.MASK
            self._state[a+1] ^= self._state[a] >> 24
            self._state[a+1] ^= self._state[c+1] >> 8
            self._state[a+1] ^= (self._state[b+1] >> 11) & SFMT.MSK2
            self._state[a+1] ^= (self._state[c+2] << 24) & SFMT.MASK
            self._state[a+1] ^= (self._state[d+1] << 18) & SFMT.MASK

            self._state[a] ^= (self._state[a] << 8) & SFMT.MASK
            self._state[a] ^= self._state[c] >> 8
            self._state[a] ^= (self._state[b] >> 11) & SFMT.MSK1
            self._state[a] ^= (self._state[c+1] << 24) & SFMT.MASK
            self._state[a] ^= (self._state[d] << 18) & SFMT.MASK
			
            a, b, c, d = a+4, (b+4) % SFMT.N, d, a
    
    @staticmethod
    def untwist(state):
        a, b, c, d = SFMT.N-4, SFMT.B-4, SFMT.C-4, SFMT.D-4

        while a >= 0:
            state[a] ^= (state[d] << 18) & SFMT.MASK
            state[a] ^= (state[c+1] << 24) & SFMT.MASK
            state[a] ^= (state[b] >> 11) & SFMT.MSK1
            state[a] ^= state[c] >> 8
            state[a] = reverse_lshift_xor_mask(state[a], 8)

            state[a+1] ^= (state[d+1] << 18) & SFMT.MASK
            state[a+1] ^= (state[c+2] << 24) & SFMT.MASK
            state[a+1] ^= (state[b+1] >> 11) & SFMT.MSK2
            state[a+1] ^= state[c+1] >> 8
            state[a+1] ^= state[a] >> 24
            state[a+1] = reverse_lshift_xor_mask(state[a+1], 8)

            state[a+2] ^= (state[d+2] << 18) & SFMT.MASK
            state[a+2] ^= (state[c+3] << 24) & SFMT.MASK
            state[a+2] ^= (state[b+2] >> 11) & SFMT.MSK3
            state[a+2] ^= state[c+2] >> 8
            state[a+2] ^= state[a+1] >> 24
            state[a+2] = reverse_lshift_xor_mask(state[a+2], 8)

            state[a+3] ^= (state[d+3] << 18) & SFMT.MASK
            state[a+3] ^= (state[b+3] >> 11) & SFMT.MSK4
            state[a+3] ^= state[c+3] >> 8
            state[a+3] ^= state[a+2] >> 24
            state[a+3] = reverse_lshift_xor_mask(state[a+3], 8)

            a, b, c, d = a-4, (b-4) % SFMT.N, (c-4) % SFMT.N, (d-4) % SFMT.N
    
        return state
    
    @staticmethod
    def recover_seed_from_state(state, min_advc=0, max_advc=10_000):
        for _ in range(min_advc // SFMT.N):
            state = SFMT.untwist(state)
        for _ in range((max_advc // SFMT.N) + 1):
            s4, s5 = state[4], state[5]
            state = SFMT.untwist(state)
            seed = MT.reverse_init_loop(state[4], 4)
            test = SFMT(seed)
            if test._state[4] == s4 and test._state[5] == s5:
                return seed
        return -1
               
if __name__ == "__main__":
    from random import randrange

    lim = 1 << 32

    '''test = SFMT(0x12345678)
    for _ in range(100):
        print(hex(test.next()))'''

    '''for _ in range(1_000):
        seed = randrange(0, lim)
        rng = SFMT(seed)
        a = rng.state
        rng.advance(624)
        b = rng.state

        a_ = SFMT.untwist(b)

        if a != a_:
            print(hex(seed))'''
    
    '''for _ in range(1_000):
        seed = randrange(0, lim)
        advc = randrange(0, 10_000)
        sfmt = SFMT(seed)
        sfmt.advance(advc)
        test = SFMT.recover_seed_from_state(sfmt.state)
        
        if test != seed:
            print(hex(seed))'''
    
    seed = randrange(0, lim)
    advc = randrange(0, 1_000_000)
    
    sfmt = SFMT(seed)
    sfmt.advance(advc)
    
    test = SFMT.recover_seed_from_state(sfmt.state, max_advc=1_000_000)

    print(f"Expected: {seed:08X} | Result: {test:08X} | Advances: {advc}")