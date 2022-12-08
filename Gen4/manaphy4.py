### Script to search for rerolled Manaphy with specific ivs and nature ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import ARNG, lcrng_recover_ivs_seeds, lcrng_prev
from Util import get_psv, get_nature, get_psv, format_ivs, get_hp_type, get_hp_damage

def get_new_pid(pid):
    psv = get_psv(pid)
    rng = ARNG(pid)
    while 1:
        pid = rng.next()
        if get_psv(pid) != psv:
            break
    return pid

def search_manaphy(min_ivs, max_ivs, target_natures):
    fmt = "Seed: {:08X} | PID: {:08X} {:9s} -> {:08X} {:9s} | PSV: {:04d} | IVs: {} | HP: {} {}"

    res = False
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for s in lcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
                                seed = lcrng_prev(s)
                                pid1 = (s & 0xffff0000) | (seed >> 16)
                                nat1 = get_nature(pid1)
                                pid2 = get_new_pid(pid1)
                                nat2 = get_nature(pid2)
                                if nat2 in target_natures:
                                    res = True
                                    seed = lcrng_prev(seed)
                                    psv = get_psv(pid1)
                                    ivs = (hp, atk, dfs, spa, spd, spe)
                                    hp_type = get_hp_type(ivs)
                                    hp_dmge = get_hp_damage(ivs)
                                    print(fmt.format(seed, pid1, f"({nat1})", pid2, f"({nat2})", psv, format_ivs(ivs), hp_type, hp_dmge))
    if not res:
        print("no results :(")

if __name__ == "__main__":
    min_ivs = (31, 0, 30, 31, 30, 31)
    max_ivs = (31, 0, 31, 31, 31, 31)
    target_natures = ("Modest", "Timid")

    search_manaphy(min_ivs, max_ivs, target_natures)