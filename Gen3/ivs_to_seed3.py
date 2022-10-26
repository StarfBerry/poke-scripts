import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, LCRNGR, GCRNG, GCRNGR, lcrng_recover_ivs_seeds, lcrng_recover_ivs_seeds_2, gcrng_recover_ivs_seeds
from jirachi3 import JirachiChannel
from Util import Pokemon
from enum import Enum

class Method(Enum):
    Method1 = (0, 0, 0) # [PIDL] [PIDH] [IV1] [IV2]
    Method2 = (0, 1, 0) # [PIDL] [PIDH] [Blank] [IV1] [IV2]
    Method3 = (1, 0, 0) # [PIDL] [Blank] [PIDH] [IV1] [IV2]
    Method4 = (0, 0, 1) # [PIDL] [PIDH] [IV1] [Blank] [IV2]
    Method1Reverse = (0, 0, 0, -1) # [PIDH] [PIDL] [IV1] [IV2]

    GameCube = 6 # [IV1] [IV2] [Ability] [PIDH] [PIDL]
    Channel  = 7 # [PIDH] [PIDL] [Blank]*3 [HP] [Atk] [Def] [Spe] [Spa] [Spd]

def ivs_to_pkm_3(hp, atk, dfs, spa, spd, spe, method=Method.Method1):
    ivs = [hp, atk, dfs, spa, spd, spe]
    
    if method != Method.Method4:
        seeds = lcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)
    else:
        seeds = lcrng_recover_ivs_seeds_2(hp, atk, dfs, spa, spd, spe)
    
    a, b = method.value[0], method.value[1]
    
    res = []
    for seed in seeds:        
        origin_seed = LCRNGR(seed).advance(2 + a + b)
        rng = LCRNG(origin_seed)

        pidl = rng.next_u16()
        pidh = rng.advance(1 + a) >> 16
        
        if method == Method.Method1Reverse:
            pidh, pidl = pidl, pidh
        
        res.append(Pokemon(pidh=pidh, pidl=pidl, ivs=ivs, seed=origin_seed))
    
    return res

def gc_ivs_to_pkm(hp, atk, dfs, spa, spd, spe):
    ivs = [hp, atk, dfs, spa, spd, spe]
    
    res = []
    for seed in gcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
        rng = GCRNG(seed)
        
        ability = (rng.advance(3) >> 16) & 1        
        
        pidh = rng.next_u16()
        pidl = rng.next_u16()
 
        res.append(Pokemon(pidh=pidh, pidl=pidl, ivs=ivs, ability=ability, seed=seed))
    
    return res

def search_pkm_3(min_ivs, max_ivs, target_natures, method):
    if method == Method.GameCube:
        get_pkm = lambda hp, atk, dfs, spa, spd, spe: gc_ivs_to_pkm(hp, atk, dfs, spa, spd, spe)
    elif method == Method.Channel:
        get_pkm = lambda hp, atk, dfs, spa, spd, spe: JirachiChannel.ivs_to_jirachi(hp, atk, dfs, spa, spd, spe)
    else:
        get_pkm = lambda hp, atk, dfs, spa, spd, spe: ivs_to_pkm_3(hp, atk, dfs, spa, spd, spe, method)
    
    res = False
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for pkm in get_pkm(hp, atk, dfs, spa, spd, spe):
                                if pkm.nature in target_natures:
                                    print(pkm)
                                    res = True
    
    if not res:
        print("no results :(")
    
if __name__ == "__main__":
    min_ivs = (31, 31, 31, 0, 31, 31)
    max_ivs = (31, 31, 31, 31, 31, 31)
    target_natures = ("Jolly", "Adamant")
    method = Method.Method1

    search_pkm_3(min_ivs, max_ivs, target_natures, method)