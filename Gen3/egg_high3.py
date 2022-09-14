'''
Script to generate seeds to get target pidh + ivs for breeding rng in RS and FRLG.
Useful if you want a custom pid + specific ivs (to make hex speak pun or replicate PCNY events xP)
To make a custom pid, you have to setup the 16bit low beforehand (e.g. with egg_low_3.py).
'''

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, LCRNGR
from Util import get_ivs, compare_ivs_egg
from enum import Enum

class EggMethods(Enum):
    Normal    = (1, 0, 1)
    Split     = (0, 1, 1)
    Alternate = (1, 0, 2)
    Mixed     = (0, 0, 2)

def generate_egg_ivs(seed, method):
    rng = LCRNG(seed)
    
    rng.advance(method[0])
    iv1 = rng.rand()
    rng.advance(method[1])
    iv2 = rng.rand()
    ivs = get_ivs(iv1, iv2)

    rng.advance(method[2])
    inh = [rng.rand() for _ in range(3)]
    par = [rng.rand() for _ in range(3)]
    
    a = [0, 1, 2, 5, 3, 4]
    for i in range(3):
        stat = a[inh[i] % (6-i)]
        ivs[stat] = 'B' if par[i] & 1 else 'A'
        a.remove(stat)
    
    return ivs

def generate_all_methods(seed):
    return [generate_egg_ivs(seed, method.value) for method in EggMethods]
    
if __name__ == "__main__":
    from Util import ask_int, u16

    high = u16(ask_int("PID High: 0x", 16))
    target_ivs = []
    while len(target_ivs) != 6:
        target_ivs = [int(iv) for iv in input("IVs (x.x.x.x.x.x): ").split(".")]

    print("\n| {:^8} | {:^24} | {:^9} |".format("Seed", "IVs", "Method"))
    print("-" * 51)
    fmt = "| {:08X} | {} | {:9} |"

    start = high << 16
    end = start + 0x10000
   
    for seed in range(start, end):
        egg_ivs = generate_all_methods(seed)
        for i, method in enumerate(EggMethods):
            if compare_ivs_egg(egg_ivs[i], target_ivs):
                ivs_f = str([f"{iv:>2}" for iv in egg_ivs[i]]).replace("'", "")
                print(fmt.format(LCRNGR(seed).next(), ivs_f, method.name))
    
    print("-" * 51)