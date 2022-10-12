### Script to search for rerolled Manaphy with specific ivs and nature ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import ARNG, LCRNGR, lcrng_recover_ivs_seeds
from Util import get_psv, get_nature, format_ivs

def get_new_pid(pid):
    psv = get_psv(pid)
    rng = ARNG(pid)
    while psv == get_psv(pid):
        pid = rng.next()
    return pid

def search_manaphy(min_ivs, max_ivs, target_natures):
    fmt = "Seed: {:08X} | PID: {:08X} {:9s} -> {:08X} {:9s} | IVs: {}"

    res = False
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for s in lcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
                                h = s >> 16
                                rng = LCRNGR(s)
                                l = rng.rand()
                                pid1 = (h << 16) | l
                                nat1 = get_nature(pid1)
                                pid2 = get_new_pid(pid1)
                                nat2 = get_nature(pid2)
                                if nat2 in target_natures and nat1 != nat2:
                                    res = True
                                    seed = rng.next()
                                    ivs = (hp, atk, dfs, spa, spd, spe)
                                    print(fmt.format(seed, pid1, f"({nat1})", pid2, f"({nat2})", format_ivs(ivs)))
    if not res:
        print("no results :(")

if __name__ == "__main__":
    min_ivs = (31, 0, 31, 31, 31, 31)
    max_ivs = (31, 31, 31, 31, 31, 31)
    target_natures = ("Modest", "Timid")

    search_manaphy(min_ivs, max_ivs, target_natures)