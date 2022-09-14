import os, sys
path = os.path.dirname(__file__)
sys.path.append(path)
sys.path.append(path + "\..")

from Util.Bits import reverse_lshift_xor_mask, reverse_rshift_xor_mask
from Matrix_GF2.GF2 import xorshift_jump_poly

class Xorshift:
    def __init__(self, s0, s1, state=None):
        if state is not None:
            self.state = state.copy()
        else:                               
            self._state = [0] * 4
            self._state[0] = s0 >> 32
            self._state[1] = s0 & 0xffffffff
            self._state[2] = s1 >> 32
            self._state[3] = s1 & 0xffffffff
    
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
        t ^= t >> 8
        t ^= self._state[3] ^ (self._state[3] >> 19)

        self._state[0] = self._state[1]
        self._state[1] = self._state[2]
        self._state[2] = self._state[3]
        self._state[3] = t

        return ((t % 0xffffffff) + 0x80000000) & 0xffffffff
    
    def prev(self):
        t = self._state[3]
        t ^= self._state[2] ^ (self._state[2] >> 19)
        t = reverse_rshift_xor_mask(t, 8)
        t = reverse_lshift_xor_mask(t, 11)

        self._state[3] = self._state[2]
        self._state[2] = self._state[1]
        self._state[1] = self._state[0]
        self._state[0] = t

        return ((self._state[3] % 0xffffffff) + 0x80000000) & 0xffffffff
    
    def jump_ahead(self, n):
        jump = xorshift_jump_poly(n)
        s0 = s1 = s2 = s3 = 0 

        while jump:
            if jump & 1:
                s0 ^= self._state[0]
                s1 ^= self._state[1]
                s2 ^= self._state[2]
                s3 ^= self._state[3]
            
            self.next()
            jump >>= 1
        
        self._state = [s0, s1, s2, s3]

    def advance(self, n=1):
        for _ in range(n):
            self.next()
    
    def back(self, n=1):
        for _ in range(n):
            self.prev()
    
    def rand(self, n):
        return self.next() % n
    
    def prev_rand(self, n):
        return self.prev() % n
    
    def clone(self):
        return Xorshift(state=self._state)

if __name__ == "__main__":
    from random import randrange

    lim = 1 << 64

    '''s0 = randrange(0, lim)
    s1 = randrange(0, lim)
    it = 10_000

    rng = Xorshift(s0, s1)

    a = [rng.next() for _ in range(it)]
    rng.next()
    b = [rng.prev() for _ in range(it)]
    b.reverse()

    print(a == b)'''

    s0 = randrange(0, lim)
    s1 = randrange(0, lim)
    a = 12_345_678

    rng1 = Xorshift(s0, s1)
    rng1.advance(a)

    rng2 = Xorshift(s0, s1)
    rng2.jump_ahead(a)

    print(hex(rng1.state))
    print(hex(rng2.state))