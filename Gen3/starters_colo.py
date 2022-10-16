import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import GCRNG, GCRNGR, gcrng_recover_pid_seeds, gcrng_recover_ivs_seeds, gcrng_prev
from Util import Pokemon

class StartersColo:
    def __init__(self, seed=0):        
        self.seed = seed
        rng = GCRNG(seed)

        self.tid = rng.rand()
        self.sid = rng.rand()

        starters = []
        for _ in range(2):
            rng.advance(2)

            iv1 = rng.rand()
            iv2 = rng.rand()
        
            ability = rng.rand() & 1

            while 1:
                pidh = rng.rand()
                pidl = rng.rand()
                xor = pidh ^ pidl ^ self.tid ^ self.sid

                if (pidl & 0xff) >= 32 and xor >= 8: # male and not shiny
                    break         
            
            starters.append(Pokemon(iv1=iv1, iv2=iv2, ability=ability, pidh=pidh, pidl=pidl))

        self.umbreon = starters[0]
        self.espeon = starters[1]
        
        self.accessible = is_accessible_in_name_screen(GCRNGR(seed).advance(1000))

    def __repr__(self):
        out = f"Seed: {self.seed:08X} | TID/SID: {self.tid:05d}/{self.sid:05d} | Accessible: {self.accessible}\n"
        out += f"Umbreon -> {self.umbreon}\n"
        out += f"Espeon  -> {self.espeon}"
        return out
    
    @staticmethod
    def ivs_to_umbreon(hp, atk, dfs, spa, spd, spe):
        seeds = gcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)
        return [StartersColo(GCRNGR(seed).advance(4)) for seed in seeds]
    
    @staticmethod
    def ivs_to_espeon(hp, atk, dfs, spa, spd, spe):
        seeds = gcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)

        res = []
        for seed in seeds:
            rng = GCRNGR(seed)
            
            pidl = rng.advance(2) >> 16
            pidh = rng.rand()

            tid, sid = reverse_tid_sid_from_pid_gen(rng.state)
            xor = tid ^ sid ^ pidh ^ pidl

            # if the first reversed Umbreon's pid is not valid, the ivs cannot be obtained with this seed
            if (pidl & 0xff) >= 32 and xor >= 8:            
                seed_ = GCRNGR(rng.state).advance(8)
                res.append(StartersColo(seed_))
                
                # check if there was one or several rerolls before the valid pid
                while 1:
                    pidl = rng.rand()
                    pidh = rng.rand()

                    tid, sid = reverse_tid_sid_from_pid_gen(rng.state)
                    xor = tid ^ sid ^ pidh ^ pidl
                    
                    if (pidl & 0xff) < 32 or xor < 8:
                        seed_ = GCRNGR(rng.state).advance(8)
                        res.append(StartersColo(seed_))
                    else:
                        break

        return res

    @staticmethod
    def tidsid_to_starters(tid, sid):
        seeds = gcrng_recover_pid_seeds((tid << 16) | sid)
        return [StartersColo(seed) for seed in seeds]

def reverse_tid_sid_from_pid_gen(seed):
    rng = GCRNGR(seed)
    rng.advance(5)
    sid = rng.rand()
    tid = rng.rand()
    return (tid, sid)

# Some seeds are skipped on the name input screen
# https://github.com/yatsuna827/PokemonCoRNGLibrary/blob/e1fdb0931274642904b1534b8eef378e01b87557/PokemonCoRNGLibrary/Util/LCGExtensions.cs#L15
def is_accessible_in_name_screen(seed):
    inf, sup = 0x1999ffff, 0x199a0000

    rng = GCRNGR(seed)

    prev1 = seed > inf
    prev2 = rng.next() > inf
    prev3 = rng.next() > inf
    prev4 = rng.next() > inf

    if prev1 and prev2 and prev3 and prev4: 
        return True
    
    if rng.next() < sup and is_accessible_in_name_screen(gcrng_prev(rng.state)):
        return True
    
    if rng.next() < sup and prev1 and is_accessible_in_name_screen(gcrng_prev(rng.state)):
        return True
    
    if rng.next() < sup and prev1 and prev2 and is_accessible_in_name_screen(gcrng_prev(rng.state)):
        return True
    
    if rng.next() < sup and prev1 and prev2 and prev3 and is_accessible_in_name_screen(gcrng_prev(rng.state)):
        return True
    
    return False

def search_starter_colo(min_ivs, max_ivs, target_natures, umbreon=True):
    if umbreon:
        get_pkm = lambda hp, atk, dfs, spa, spd, spe: StartersColo.ivs_to_umbreon(hp, atk, dfs, spa, spd, spe)
        get_nat = lambda starters: starters.umbreon.nature
    else:
        get_pkm = lambda hp, atk, dfs, spa, spd, spe: StartersColo.ivs_to_espeon(hp, atk, dfs, spa, spd, spe)
        get_nat = lambda starters: starters.espeon.nature

    res = False
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for pkm in get_pkm(hp, atk, dfs, spa, spd, spe):
                                if get_nat(pkm) in target_natures:
                                    res = True
                                    print(pkm)
                                    print("######################")
    
    if not res:
        print("No resutls :(")

if __name__ == "__main__":
    min_ivs = [31, 0, 31, 31, 31, 31]
    max_ivs = [31, 31, 31, 31, 31, 31]
    target_natures = ("Timid", "Modest", "Calm", "Bold")
    
    #test = StartersColo.tidsid_to_starters(9887, 27329)
    #test = StartersColo.tidsid_to_starters(63309, 30809)   
    
    #test = StartersColo.ivs_to_umbreon(*max_ivs)
    #test = StartersColo.ivs_to_espeon(*min_ivs)
    #test = StartersColo.ivs_to_espeon(1, 1, 1, 1, 1, 1)
    
    
    '''for res in test:
        print(res)
        print("######################")'''
    
    search_starter_colo(min_ivs, max_ivs, target_natures, False)