### Script to mess with Jirachi rng in Gen 3 games ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, GCRNG, GCRNGR, gcrng_recover_pid_seeds, channel_recover_ivs_seeds
from Util import get_ivs, get_nature, format_ivs, compare_ivs

class JirachiColo:
    tid = 20043
    berries = ("Salac", "Ganlon")
    
    def __init__(self, seed=0):
        self.seed = seed & 0xffff
        rng = LCRNG(self.seed)

        h = rng.next_u16()
        l = rng.next_u16()
        self.pid = (h << 16) | l
        
        self.nature = get_nature(self.pid)
        self.shiny = (self.tid ^ h ^ l) < 8 # sid = 0

        iv1 = rng.next_u16()
        iv2 = rng.next_u16()
        self.ivs = get_ivs(iv1, iv2)

        self.berry = (rng.next_u16() // 3) & 1
    
    def __repr__(self):
        out = f"Seed: {self.seed:04X} | "
        out += f"PID: {self.pid:08X} | "
        out += f"Nature: {self.nature:7s} | "
        out += f"IVs: {format_ivs(self.ivs)} | "
        out += f"Shiny: {self.shiny} | "
        out += f"Berry: {JirachiColo.berries[self.berry]}"
        return out

class JirachiChannel:
    tid = 40122
    games = ("Ruby", "Sapphire")
    genders = ("Female", "Male")

    def __init__(self, seed=0):
        self.seed = seed & 0xffffffff
        rng = GCRNG(self.seed)

        self.sid = rng.next_u16()
        
        h = rng.next_u16()
        l = rng.next_u16()
        
        if (self.tid ^ self.sid ^ h ^ (l < 8)) != 0: # shiny lock failed
            h ^= 0x8000
        
        self.pid = (h << 16) | l
        self.nature = get_nature(self.pid)
        self.shiny = (self.tid ^ self.sid ^ h ^ l) < 8

        self.berry = (rng.next() >> 29) > 3
        self.game = (rng.next() >> 28) > 7
        self.ot_gender = (rng.next() >> 27) > 15

        hp, atk, dfs, spe, spa, spd = (rng.next() >> 27 for _ in range(6))
        self.ivs = [hp, atk, dfs, spa, spd, spe]

        self.accessible = JirachiChannel.validate_jirachi(self.seed)
    
    @staticmethod
    def ivs_to_jirachi(hp, atk, dfs, spa, spd, spe):
        seeds = channel_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)
        return [JirachiChannel(GCRNGR(seed).advance(7)) for seed in seeds]
    
    @staticmethod
    def pid_to_jirachi(pid):
        h = pid >> 16
        l = pid & 0xffff
        seeds = []

        for seed in gcrng_recover_pid_seeds(pid):
            sid = seed >> 16
            if (40122 ^ sid ^ h ^ (l < 8)) == 0:
                seeds.append(seed)

        for seed in gcrng_recover_pid_seeds(pid ^ 0x80000000):
            sid = seed >> 16
            if (40122 ^ sid ^ h ^ (l < 8)) != 0:
                seeds.append(seed)
        
        return [JirachiChannel(GCRNGR(seed).next()) for seed in seeds]

    # https://github.com/Admiral-Fish/PokeFinder/blob/d2b11e3c2821d018c82dfbb044424717abaef2d4/Source/Core/Gen3/Searchers/GameCubeSearcher.cpp#L448
    @staticmethod
    def validate_jirachi(seed):
        rng = GCRNGR(seed)

        num1, num2, num3 = (rng.next_u16() for _ in range(3))

        rng.advance(3)
        if num1 <= 0x4000 and JirachiChannel.validate_menu(rng.state):
            return True
        
        rng.advance(1)
        if num2 > 0x4000 and num1 <= 0x547a and JirachiChannel.validate_menu(rng.state):
            return True
        
        rng.advance(1)
        if num3 > 0x4000 and num2 > 0x547a and JirachiChannel.validate_menu(rng.state):
            return True
        
        return False
    
    # https://github.com/Admiral-Fish/PokeFinder/blob/d2b11e3c2821d018c82dfbb044424717abaef2d4/Source/Core/Gen3/Searchers/GameCubeSearcher.cpp#L486
    @staticmethod
    def validate_menu(seed):        
        target = seed >> 30
        
        if target == 0:
            return False
        
        rng = GCRNGR(seed)
        mask = 1 << target

        while (mask & 14) != 14:
            num = rng.next() >> 30
            if num == target:
                return False
            
            mask |= 1 << num
        
        return True

    def __repr__(self):
        out = f"Seed: {self.seed:08X} | "
        out += f"TID/SID: {self.tid:05d}/{self.sid:05d} | "
        out += f"PID: {self.pid:08X} | "
        out += f"Nature: {self.nature:7s} | "
        out += f"IVs: {format_ivs(self.ivs)} | "
        out += f"Shiny: {str(self.shiny):5s} | "
        out += f"Berry: {JirachiColo.berries[self.berry]:6s} | "
        out += f"Game: {JirachiChannel.games[self.game]:8s} | "
        out += f"OT Gender: {JirachiChannel.genders[self.ot_gender]:6s} | "
        out += f"Accessible: {self.accessible}"
        return out
        
def search_ivs_wishmkr_jirachi(min_ivs, max_ivs):
    for seed in range(0x10000):
        jirachi = JirachiColo(seed)
        if compare_ivs(min_ivs, max_ivs, jirachi.ivs):
            print(jirachi)

def search_shiny_wishmkr_jirachi():
    for seed in range(0x10000):
        jirachi = JirachiColo(seed)
        if jirachi.shiny:
            print(jirachi)

# why not ?
def search_not_xored_shiny_channel_jirachi():
    c = 0
    for sid in range(0x10000):       
        val = (sid << 16) | (40122 ^ sid)
        
        for s in gcrng_recover_pid_seeds(val):
            c += (GCRNG(s).advance(3) >> 16) >= 8 # cannot be shiny in this context
        
        for s in gcrng_recover_pid_seeds(val ^ 1):
            if (GCRNG(s).advance(3) >> 16) < 8:
                jirachi = JirachiChannel(s) # always shiny here
                print(jirachi)
                c += 1

    print(f"Total not xored Jirachi: {c}")

if __name__ == "__main__":
    min_ivs = (27, 27, 27, 0, 27, 27)
    max_ivs = (31, 31, 31, 31, 31, 31)
    
    #search_ivs_wishmkr_jirachi(min_ivs, max_ivs)    
   
    '''test = JirachiChannel.ivs_to_jirachi(*max_ivs)
    for jirachi in test:
        print(jirachi)'''

    '''test = JirachiChannel.pid_to_jirachi(0xdeadbeef)
    for jirachi in test:
        print(jirachi)'''
    
    #search_shiny_wishmkr_jirachi()
    
    search_not_xored_shiny_channel_jirachi()