import sys
sys.path.append('.')

from Util import reverse_lshift_xor_mask, reverse_rshift_xor_mask

class Xorshift:
    def __init__(self, s0, s1, state=None):
        if state is not None:
            self.state = state
        else:
            self.state = [0] * 4
            self.state[0] = s0 >> 32
            self.state[1] = s0 & 0xffffffff
            self.state[2] = s1 >> 32
            self.state[3] = s1 & 0xffffffff
    
    def state(self):
        return (self.state[0] << 96) | (self.state[1] << 64) | (self.state[2] << 32) | self.state[3]
    
    def states(self):
        s0 = (self.state[0] << 32) | self.state[1]
        s1 = (self.state[2] << 32) | self.state[3]
        return s0, s1
        
    def next(self):
        t = self.state[0]
        t ^= (t << 11) & 0xffffffff
        t ^= t >> 8
        t ^= self.state[3] ^ (self.state[3] >> 19)

        self.state[0] = self.state[1]
        self.state[1] = self.state[2]
        self.state[2] = self.state[3]
        self.state[3] = t

        return ((t % 0xffffffff) + 0x80000000) & 0xffffffff
    
    def prev(self):
        t = self.state[3]
        t ^= self.state[2] ^ (self.state[2] >> 19)
        t = reverse_rshift_xor_mask(t, 8)
        t = reverse_lshift_xor_mask(t, 11)

        self.state[3] = self.state[2]
        self.state[2] = self.state[1]
        self.state[1] = self.state[0]
        self.state[0] = t

        return ((self.state[3] % 0xffffffff) + 0x80000000) & 0xffffffff
    
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
        return Xorshift(state=self.state.copy())

if __name__ == "__main__":
    from random import randrange

    lim = 1 << 64

    s0 = randrange(0, lim)
    s1 = randrange(0, lim)
    it = 10_000

    rng = Xorshift(s0, s1)

    a = [rng.next() for _ in range(it)]
    rng.next()
    b = [rng.prev() for _ in range(it)]
    b.reverse()

    print(a == b)