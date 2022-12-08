def compute_jump_table(mul, add, size=32):
    MUL, ADD = [mul], [add]
    m = 1 << size
    for i in range(1, size):
        MUL.append(MUL[i-1]**2 % m)
        ADD.append(ADD[i-1] * (MUL[i-1] + 1) % m)
    return (MUL, ADD)

class LCRNG:   
    MASK = 0xFFFFFFFF
    BITS = 32
    
    MUL, ADD = compute_jump_table(0x41C64E6D, 0x6073)

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
    
    def next_u16(self):
        return self.next() >> 16

    def rand(self, lim):
        return self.next_u16() % lim

    def advance(self, n):
        for _ in range(n):
            self._state = (self._state * self.MUL[0] + self.ADD[0]) & self.MASK
        return self._state

    def jump(self, n):              
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
    MUL, ADD = compute_jump_table(0xEEB9EB65, 0xA3561A1)

class MRNG(LCRNG):   
    MUL, ADD = compute_jump_table(0x41C64E6D, 0x3039)

class MRNGR(LCRNG):   
    MUL, ADD = compute_jump_table(0xEEB9EB65, 0xFC77A683)

class GCRNG(LCRNG):    
    MUL, ADD = compute_jump_table(0x343FD, 0x269EC3)

class GCRNGR(LCRNG):    
    MUL, ADD = compute_jump_table(0xB9B33155, 0xA170F641)

class ARNG(LCRNG):    
    MUL, ADD = compute_jump_table(0x6C078965, 0x1)

class ARNGR(LCRNG):
    MUL, ADD = compute_jump_table(0x9638806D, 0x69C77F93)

class BWRNG(LCRNG):
    MASK = 0xFFFFFFFFFFFFFFFF
    BITS = 64

    MUL, ADD = compute_jump_table(0x5D588B656C078965, 0x269EC3, 64)
    
    def next_u16(self):
        return self.next() >> 48
    
    def next_u32(self):
        return self.next() >> 32

    def rand(self, lim):
        return (self.next_u32() * lim) >> 32
    
class BWRNGR(BWRNG):
    MUL, ADD = compute_jump_table(0xDEDCEDAE9638806D, 0x9B1AE6E9A384E6F9, 64)