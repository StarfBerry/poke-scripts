import sys
sys.path.append('.')

from Util import reverse_lshift_xor_mask, reverse_rshift_xor_mask

class TinyMT:
    A = 0x8F7011EE
    B = 0xFC78FF1F
    C = 0x3793FDFF
    M = 0x6C078965

    MASK = 0xFFFFFFFF
    
    def __init__(self, seed=0, state=None):
        if state is not None:
            self._state = state
            self._period_certification()
        else:
            self._state = [seed & self.MASK, TinyMT.A, TinyMT.B, TinyMT.C]
            for i in range(1, 8):
                self._state[i & 3] ^= (TinyMT.M * (self.state[(i - 1) & 3] ^ (self.state[(i - 1) & 3] >> 30)) + i) & self.MASK
            
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

        x ^= (x << 1) & self.MASK
        y ^= (y >> 1) ^ x

        self._state[0] = self._state[1]
        self._state[1] = self._state[2]
        self._state[2] = x ^ (y << 10) & self.MASK
        self._state[3] = y

        if y & 1:
            self._state[1] ^= TinyMT.A
            self._state[2] ^= TinyMT.B
            
    def _prev_state(self):
        y = self._state[3]
        x = self._state[2] ^ (y << 10) & self.MASK

        self._state[2] = self._state[1]
        self._state[1] = self._state[0]

        if y & 1:
            self._state[2] ^= TinyMT.A
            x ^= TinyMT.B

        y = reverse_rshift_xor_mask(y ^ x)
        x = reverse_lshift_xor_mask(x)

        self._state[3] = y
        self._state[0] = x ^ self._state[1] ^ self._state[2]
        
        _x = (self._state[2] ^ (y << 10) ^ (y & 1) * TinyMT.B) & self.MASK
        xor = (self._state[1] >> 31) ^ (y >> 31) ^ (y & 1)
        xor ^= (reverse_rshift_xor_mask(y ^ _x) >> 31) ^ ((reverse_lshift_xor_mask(_x) >> 30) & 1)

        if xor:
            self._state[0] ^= 0x80000000

    def _temper(self):
        t = (self._state[0] + (self._state[2] >> 8)) & self.MASK
        return self._state[3] ^ t ^ (t & 1) * TinyMT.C
    
    def _period_certification(self):
        if self._state[0] & 0x7fffffff == 0 and self._state[1] == 0 and self._state[2] == 0 and self._state[3] == 0:
            self._state = [ord('T'), ord('I'), ord('N'), ord('Y')]
       
    @staticmethod
    def recover_seed_from_state(state, min_advc=0, max_advc=10_000):
        rng = TinyMT(state=state)
        rng.back(8+min_advc) # advances of 8 in the constructor
        
        for _ in range(max_advc):
            s = rng.state

            for i in range(7, 0, -1):
                s[i & 3] ^= (TinyMT.M * (s[(i - 1) & 3] ^ (s[(i - 1) & 3] >> 30)) + i) & TinyMT.MASK
            
            if s[3] == TinyMT.C:
                if s[1] == TinyMT.A and s[2] == TinyMT.B:
                    return s[0]
                
                c = rng.state
                c[0] ^= 0x80000000
                
                for i in range(7, 0, -1):
                    c[i & 3] ^= (TinyMT.M * (c[(i - 1) & 3] ^ (c[(i - 1) & 3] >> 30)) + i) & TinyMT.MASK
                
                if c[1] == TinyMT.A and c[2] == TinyMT.B:
                    return c[0]
            
            rng.back()
        
        return -1
          
    @staticmethod
    def backward(state, n=1):
        rng = TinyMT(state=state)
        rng.back(n)
        return rng.state

if __name__ == "__main__":
    from random import randrange

    seed = randrange(0, 1 << 32)
    rng = TinyMT(seed)
    it = 10_000

    a = [rng.next() for _ in range(it)]
    rng.next()

    b = [rng.prev() for _ in range(it)]
    b.reverse()

    print(a == b)

    s = randrange(0, 1 << 32)
    a = randrange(0, 10000)
    
    tinymt = TinyMT(s)
    tinymt.advance(a)
    
    r = TinyMT.recover_seed_from_state(tinymt.state)
    
    print(f"Recovered Seed: {r:08X} | Seed: {s:08X}")