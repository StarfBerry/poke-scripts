import sys
sys.path.append(".")
sys.path.append("../")

import z3
from Util import reverse_lshift_xor_mask, reverse_rshift_xor_mask

class MT:
    A = 0x9908B0DF
    B = 0x9D2C5680
    C = 0xEFC60000
    M = 397
    N = 624

    MASK = 0xFFFFFFFF
    
    def __init__(self, seed=0):
        self._state = [0] * MT.N

        self._state[0] = seed & MT.MASK
        for i in range(1, MT.N):
            self._state[i] = (0x6C078965 * (self._state[i-1] ^ (self._state[i-1] >> 30)) + i) & MT.MASK

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
            self._state[i] = self._state[(i + MT.M) % MT.N] ^ (x >> 1) ^ (x & 1) * MT.A

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
        x = reverse_lshift_xor_mask(x, 7, MT.B)
        return reverse_rshift_xor_mask(x, 11)
    
    @staticmethod
    def untemper_state(state):
        return [MT.untemper(state[i]) for i in range(MT.N)]

    @staticmethod
    def z3_twist(state):
        for i in range(MT.N):
            x = (state[i] & 0x80000000) + (state[(i + 1) % MT.N] & 0x7fffffff)
            y = z3.LShR(x, 1)
            y = z3.If(x & 1 == 1, y ^ MT.A, y)
            state[i] = state[(i + MT.M) % MT.N] ^ y
        
        return state

    @staticmethod
    def twist(state):
        for i in range(MT.N):
            x = (state[i] & 0x80000000) | (state[(i + 1) % MT.N] & 0x7fffffff)         
            y = x >> 1
            if x & 1:
                y ^= MT.A
            
            state[i] = state[(i + MT.M) % MT.N] ^ y
        
        return state

    @staticmethod
    def untwist(state):
        for i in range(MT.N-1, -1, -1):         
            y = state[i] ^ state[(i + MT.M) % MT.N]
            if y > 0x7fffffff: # y is a 31 bits without the xor
                y ^= MT.A
            
            prev = (y << 1) & 0x80000000

            _y = state[i-1] ^ state[(i + MT.M - 1) % 624]
            if _y > 0x7fffffff:
                _y ^= MT.A
                prev |= 1
            
            prev |= (_y << 1) & 0x7FFFFFFE 
            state[i] = prev
        
        return state
       
    @staticmethod
    def reverse_init_linear(s, i):
        s = (0x9638806D * (s - i)) & MT.MASK
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
    def recover_seed_from_state_values(u0, u227, offset=0):
        if offset < 0 or offset > 395:
            raise ValueError("0 <= offset < 396")
        
        x = u0 ^ u227
        
        s228_lsb = x >> 31
        if s228_lsb: # without the xor, x is at most a 31 bit value
            x ^= MT.A

        s227_msb = (x >> 30) & 1 # bit(s[227], 31) == bit(x, 30)
        if s227_msb: 
            x ^= 1 << 30
        
        s228_31 = (x << 1) | s228_lsb
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
    def recover_seed_from_rands(r0, r227, offset=0):
        return MT.recover_seed_from_state_values(MT.untemper(r0), MT.untemper(r227), offset)
    
    @staticmethod
    def recover_seed_from_untempered_state(state, min_advc=0, max_advc=10_000):
        for _ in range(min_advc // MT.N):
            state = MT.untwist(state)
        for _ in range((max_advc // MT.N) + 1):
            seed = MT.recover_seed_from_state_values(state[0], state[227])
            if seed != -1:
                return seed
            state = MT.untwist(state)
        return -1
    
    @staticmethod
    def recover_seed_from_tempered_state(state, min_advc=0, max_advc=10_000):
        return MT.recover_seed_from_untempered_state(MT.untemper_state(state), min_advc, max_advc)

    @staticmethod
    def recover_seed_from_consecutive_outputs(outputs):        
        if not 1 < len(outputs) < 625:
            raise ValueError("1 < len(outputs) < 625")
        
        seed = z3.BitVec('seed', 32)
        state = [z3.BitVec(f'MT[{i}]', 32) for i in range(MT.N)]
        
        state[0] = seed
        for i in range(1, MT.N):
            tmp = 0x6C078965 * (state[i-1] ^ (z3.LShR(state[i-1], 30))) + i
            state[i] = tmp & MT.MASK
        
        state = MT.z3_twist(state)
        
        s = z3.Solver()
        for i, x in outputs:
            s.add(state[i] == MT.untemper(x))
        
        if s.check() == z3.sat:
            m = s.model()
            return m[seed].as_long()
        
        return -1

if __name__ == "__main__":
    from random import randrange
    from time import time
    
    lim = 1 << 32
       
    '''for _ in range(10_000):
        seed = randrange(0, lim)
        offset = randrange(0, 396)
        mt = MT(seed)
        test = MT.recover_seed_from_state_values(mt.state[offset], mt.state[227+offset], offset)
        if test != seed:
            print(hex(seed))'''
    
    '''for _ in range(10_000):
        seed = randrange(0, lim)
        offset = randrange(0, 396)
        mt = MT(seed)
        mt.advance(offset)
        r0 = mt.next()
        mt.advance(226)
        r227 = mt.next()
        test = MT.recover_seed_from_rands(r0, r227, offset)
        if test != seed:
            print(hex(seed))'''

    '''for _ in range(10_000):
        seed = randrange(0, lim)
        advc = randrange(1000, 10_000)
        mt = MT(seed)
        mt.advance(advc)
        test = MT.recover_seed_from_untempered_state(mt.state, advc)
        if test != seed:
            print(hex(seed))'''
    
    '''seed = randrange(0, lim)
    mt = MT(seed)
    mt.advance(624*9745)
    state = [mt.next() for _ in range(624)]
    test = MT.recover_seed_from_tempered_state(state, max_advc=6_240_000)
    print(hex(seed), hex(test))'''

    '''seed = randrange(0, lim)
    mt = MT(seed)

    state = [mt.next() for _ in range(624)]
    start = time()
    test = MT.recover_seed_from_tempered_state(state)
    print(time() - start)
    print(hex(seed), hex(test))'''

    '''it = 2
    advc = 0
    seed = randrange(0, lim)
    
    mt = MT(seed)
    mt.advance(advc)
    outputs = [(i, mt.next()) for i in range(advc, advc+it)]

    start = time()
    test = MT.recover_seed_from_consecutive_outputs(outputs)
    print("time:", time() - start)
    print(hex(seed), hex(test))'''