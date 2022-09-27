import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util.Bits import reverse_xor_lshift_mask, reverse_xor_rshift_mask

class MT:
    A = 0x9908B0DF
    B = 0x9D2C5680
    C = 0xEFC60000
    M = 397
    N = 624
    
    def __init__(self, seed=0):
        self._state = [0] * MT.N

        self._state[0] = seed & 0xffffffff
        for i in range(1, MT.N):
            self._state[i] = (0x6C078965 * (self._state[i-1] ^ (self._state[i-1] >> 30)) + i) & 0xffffffff

        self._twist()
        self._index = 0
    
    @property
    def state(self):
        return self._state.copy()
    
    def next(self):        
        if self._index == MT.N:
            self._twist()
            self._index = 0

        return self._temper()
          
    def rand(self, lim=None):       
        rnd = self.next()
        return (rnd * lim) >> 32 if lim is not None else rnd >> 16

    def advance(self, n=1):
        self._index += n

        if self._index >= MT.N:
            q, self._index = divmod(self._index, MT.N)
            for _ in range(q): 
                self._twist()
    
    def contain(self, untmp):
        return untmp in self._state

    def _twist(self):
        for i in range(MT.N):
            x = (self._state[i] & 0x80000000) | (self._state[(i + 1) % MT.N] & 0x7fffffff)
            y = x >> 1

            if x & 1:
                y ^= MT.A         
            
            self._state[i] = self._state[(i + MT.M) % MT.N] ^ y

    def _temper(self):
        x = self._state[self._index]
        self._index += 1
        x ^= x >> 11
        x ^= (x << 7) & MT.B
        x ^= (x << 15) & MT.C
        x ^= x >> 18
        return x
    
    @staticmethod
    def untemper(x):
        x ^= x >> 18
        x ^= (x << 15) & MT.C
        x = reverse_xor_lshift_mask(x, 7, MT.B)
        return reverse_xor_rshift_mask(x, 11)
    
    @staticmethod
    def untemper_state(state):
        return [MT.untemper(state[i]) for i in range(MT.N)]

    @staticmethod
    def untwist(state):
        for i in range(MT.N-1, -1, -1):         
            y = state[i] ^ state[(i + MT.M) % MT.N]
            if y > 0x7fffffff:
                y ^= MT.A
            
            prev = (y << 1) & 0x80000000

            y_ = state[i-1] ^ state[(i + MT.M - 1) % MT.N]
            if y_ > 0x7fffffff:
                y_ ^= MT.A
                prev |= 1
            
            prev |= (y_ << 1) & 0x7FFFFFFE 
            state[i] = prev
       
    @staticmethod
    def reverse_init_linear(s, i):
        s = (0x9638806D * (s - i)) & 0xffffffff
        return s ^ (s >> 30)
    
    @staticmethod
    def reverse_init_loop(s, p):
        for i in range(p, 0, -1):
            s = MT.reverse_init_linear(s, i)
        return s
       
    '''
    i = 227
    y = (s[227] & 0x80000000) | (s[228] & 0x7fffffff)
    S[227] = S[(227 + 397) % 624] ^ (y >> 1) ^ (y & 1) * 0x9908B0DF
    S[227] = S[0] ^ (y >> 1) ^ (y & 1) * 0x9908B0DF
    x = S[227] ^ S[0] = (((s[227] & 0x80000000) | (s[228] & 0x7fffffff)) >> 1) ^ (s[228] & 1) * 0x9908B0DF
    '''

    # based on: https://www.ambionics.io/blog/php-mt-rand-prediction
    @staticmethod
    def recover_seed_from_untempered_values(u0, u227, offset=0):
        if offset < 0 or offset > 395:
            raise ValueError("0 <= offset < 396")
        
        x = u0 ^ u227
        
        s228_lsb = x >> 31
        if s228_lsb: # without the xor, x is at most a 31 bit value
            x ^= MT.A

        s227_msb = (x >> 30) & 1 # bit(s[227], 31) == bit(x, 30)
        if s227_msb: 
            x ^= 1 << 30
        
        s228_31 = (x << 1) | s228_lsb # recover first 31 bits of the previous state[228]
        for msb in range(2):
            s228 = (msb << 31) | s228_31
            
            s227 = MT.reverse_init_linear(s228, 228 + offset)
            if (s227 >> 31) != s227_msb:
                continue

            seed = MT.reverse_init_loop(s228, 228 + offset)
            
            mt = MT(seed)
            if mt._state[offset] == u0:
                return seed
        
        return -1

    @staticmethod
    def recover_seed_from_tempered_values(r0, r227, offset=0):
        return MT.recover_seed_from_untempered_values(MT.untemper(r0), MT.untemper(r227), offset)
    
    @staticmethod
    def recover_seed_from_untempered_state(state, min_advc=0, max_advc=10_000):
        for _ in range(min_advc // MT.N):
            MT.untwist(state)
        
        advc = (max_advc - min_advc) // MT.N
        
        for _ in range(advc + 1):
            seed = MT.recover_seed_from_untempered_values(state[0], state[227])
            if seed != -1:
                return seed
            
            MT.untwist(state)
        
        return -1
    
    @staticmethod
    def recover_seed_from_tempered_state(state, min_advc=0, max_advc=10_000):
        return MT.recover_seed_from_untempered_state(MT.untemper_state(state), min_advc, max_advc)