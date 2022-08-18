### Script to get seeds for TID/SID in RS ###

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import lcrng_recover_lower_16bits_pid, LCRNGR
from Util import ask_int, u32
import seed3

tid = ask_int("TID: ", condition=lambda tid: 0 <= tid < 65536)
sid = ask_int("SID: ", condition=lambda sid: 0 <= sid < 65536)
tidsid = (tid << 16) | sid

seeds = lcrng_recover_lower_16bits_pid(tidsid)
if len(seeds) == 0:
    print("This IDs combo doesn't exists in RS.")
else:
    min_advc = u32(ask_int("Min Advances: "))
    max_advc = u32(ask_int("Max Advances: "))
    print()
    
    fmt = "Seed: {:04X} | Advances: {}"
    res = False
    
    for seed in seeds:
        init = seed3.get_init_seed(seed, min_advc, max_advc)
        if init[0] is not None:
            print(fmt.format(*init))
            res = True
    
    if not res:
        print("no results :(")