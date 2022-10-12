import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

import z3
from MT import MT

def z3_mt_twist(state):
    for i in range(MT.N):
        x = (state[i] & 0x80000000) + (state[(i + 1) % MT.N] & 0x7fffffff)
        y = z3.LShR(x, 1)
        y = z3.If(x & 1 == 1, y ^ MT.A, y)
        state[i] = state[(i + MT.M) % MT.N] ^ y
    
    return state

# can recover the MT seed in about a minute using only the 2 first outputs
def mt_recover_seed_from_consecutive_outputs(out):        
    if not 1 < len(out) < 625:
        raise ValueError("1 < len(outputs) < 625")
    
    seed = z3.BitVec("seed", 32)
    state = [z3.BitVec(f"MT[{i}]", 32) for i in range(624)]
    
    state[0] = seed
    for i in range(1, 624):
        tmp = 0x6c078965 * (state[i-1] ^ (z3.LShR(state[i-1], 30))) + i
        state[i] = tmp & 0xffffffff
    
    state = z3_mt_twist(state)
    
    s = z3.Solver()
    for i, x in out:
        s.add(state[i] == MT.untemper(x))
    
    if s.check() == z3.sat:
        m = s.model()
        return m[seed].as_long()
    
    return -1

if __name__ == "__main__":
    from random import randrange
    from time import time

    seed = randrange(0, 1 << 32)
    advc = 0
    it = 2
    
    mt = MT(seed)
    mt.advance(advc)

    out = [(i, mt.next()) for i in range(advc, advc+it)]
    
    start = time()
    test = mt_recover_seed_from_consecutive_outputs(out)
    
    print("time:", time() - start)
    print(hex(seed), hex(test))