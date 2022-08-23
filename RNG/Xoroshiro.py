class Xoroshiro:
    MASK = 0xFFFFFFFFFFFFFFFF
    
    def __init__(self, s0, s1=0x82A2B175229D6A5B):
       self.s0 = s0
       self.s1 = s1
    
    def state(self):
        return (self.s0 << 64) | self.s1

    def states(self):
        return self.s0, self.s1
    
    def next(self):
        s0, s1 = self.s0, self.s1
        res = (s0 + s1) & Xoroshiro.MASK
        s1 ^= s0
        
        self.s0 = Xoroshiro.rotl(s0, 24) ^ s1 ^ (s1 << 16) & Xoroshiro.MASK
        self.s1 = Xoroshiro.rotl(s1, 37)
        
        return res
    
    def prev(self):
        s1 = Xoroshiro.rotl(self.s1, 27)
        s0 = self.s0 ^ s1 ^ (s1 << 16) & Xoroshiro.MASK
        s0 = Xoroshiro.rotl(s0, 40)
        s1 ^= s0
        
        self.s0 = s0
        self.s1 = s1
        
        return (s0 + s1) & Xoroshiro.MASK
    
    def advance(self, n=1):
        for _ in range(n):
            self.next()
    
    def back(self, n=1):
        for _ in range(n):
            self.prev()

    def rand(self, n=0xffffffff):
        mask = Xoroshiro.get_mask(n)
        rnd = self.next() & mask
        while rnd >= n:
            rnd = self.next() & mask
        return rnd

    def clone(self):
        return Xoroshiro(self.s0, self.s1)
    
    @staticmethod
    def rotl(x, k):
        return ((x << k) | (x >> (64 - k))) & Xoroshiro.MASK
    
    @staticmethod
    def get_mask(x):
        x -= 1
        for i in range(6):
            x |= x >> (1 << i)
        return x

if __name__ == "__main__":
    rng = Xoroshiro(0)
    it = 10_000

    a = [rng.next() for _ in range(it)]
    b = [rng.prev() for _ in range(it)]
    b.reverse()

    print(a == b)