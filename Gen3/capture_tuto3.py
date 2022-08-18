### Script to get shiny Wally's Ralts and the Old Man's Weedle. ###

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import LCRNG
from Util import ask_int

def generate_shiny_tuto(seed, minAdvc, maxAdvc):
    print("| {:^10} | {:^5} | {:^5} | {:^8} |".format("Advances", "TID", "SID", "PID"))
    print("-" * 41)
    fmt = "| {:^10} | {:05d} | {:05d} | {:08X} |"
    
    rng = LCRNG(seed)
    rng.advance(minAdvc+3) # delay

    for advc in range(minAdvc, maxAdvc):
        tmp = LCRNG(rng.next())         
        sid = tmp.rand()
        tid = tmp.rand()
        
        pid = 0
        while (pid & 0xff) < 128: # Male only
            pidl = tmp.rand()
            pidh = tmp.rand()
            pid = (pidh << 16) | pidl
        
        xor = pidh ^ pidl ^ tid ^ sid
        if xor < 8:
            print(fmt.format(advc, tid, sid, pid))
        
    print("-" * 41)

def generate_shiny_teachytv(seed, min_advc, max_advc):
    pass

if __name__ == "__main__":
    seed = ask_int("Initial Seed: 0x", 16)
    minAdvc = ask_int("Min Advances: ")
    maxAdvc = ask_int("Max Advances: ", condition=lambda val: val > minAdvc) + 1
    print()
    generate_shiny_tuto(seed, minAdvc, maxAdvc)