import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, LCRNGR, GCRNG, GCRNGR, lcrng_recover_lower_16bits_ivs, lcrng_recover_lower_16bits_ivs_2, gcrng_recover_lower_16bits_ivs
from jirachi3 import JirachiChannel
from Util import Pokemon
from enum import Enum

class Method(Enum):
    Method1 = (0, 0, 0) # [PIDL] [PIDH] [IV1] [IV2]
    Method2 = (0, 1, 0) # [PIDL] [PIDH] [Blank] [IV1] [IV2]
    Method3 = (1, 0, 0) # [PIDL] [Blank] [PIDH] [IV1] [IV2]
    Method4 = (0, 0, 1) # [PIDL] [PIDH] [IV1] [Blank] [IV2]
    Method1Reverse = (0, 0, 0, True) # [PIDH] [PIDL] [IV1] [IV2]

    Gamecube = 5
    Channel  = 6

def ivs_to_pkmn(ivs, method=Method.Method1):
    seeds = lcrng_recover_lower_16bits_ivs(*ivs) if method != Method.Method4 else lcrng_recover_lower_16bits_ivs_2(*ivs)
    res = []
    for seed in seeds:
        iv2 = LCRNG(seed).advance(1 + method.value[2], 16)
        iv1 = seed >> 16
        rng = LCRNGR(seed)
        pidh = rng.advance(1 + method.value[1], 16)
        pidl = rng.advance(1 + method.value[0], 16)
        if method == Method.Method1Reverse: 
            pidh, pidl = pidl, pidh
        origin_seed = rng.next()
        res.append(Pokemon(pidh=pidh, pidl=pidl, iv1=iv1, iv2=iv2, seed=origin_seed))
    return res

def gc_ivs_to_pkmn(ivs):
    res = []
    for seed in gcrng_recover_lower_16bits_ivs(*ivs):
        rng = GCRNG(seed)
        iv1 = seed >> 16
        iv2 = rng.rand()
        ability = rng.rand() & 1
        pidh = rng.rand()
        pidl = rng.rand()
        origin_seed = GCRNGR(seed).next()
        res.append(Pokemon(gc=True, pidh=pidh, pidl=pidl, iv1=iv1, iv2=iv2, ability=ability, seed=origin_seed))
    return res

if __name__ == "__main__":
    min_ivs = (31, 31, 31, 0, 31, 31)
    max_ivs = (31, 31, 31, 31, 31, 31)
    method = Method.Method1
    target_natures = ("Jolly", "Adamant")

    if method == Method.Gamecube:
        get_pkmn = lambda hp, atk, dfs, spa, spd, spe: gc_ivs_to_pkmn((hp, atk, dfs, spa, spd, spe))
    elif method == Method.Channel:
        get_pkmn = lambda hp, atk, dfs, spa, spd, spe: JirachiChannel.ivs_to_jirachi(hp, atk, dfs, spa, spd, spe)
    else:
        get_pkmn = lambda hp, atk, dfs, spa, spd, spe: ivs_to_pkmn((hp, atk, dfs, spa, spd, spe), method)

    res = False
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for pkmn in get_pkmn(hp, atk, dfs, spa, spd, spe):
                                if pkmn.nature in target_natures:
                                    print(pkmn)
                                    res = True
    
    if not res:
        print("no resuts :(")