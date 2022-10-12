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

        h = rng.rand()
        l = rng.rand()
        
        self.pid = (h << 16) | l
        self.nature = get_nature(self.pid)
        self.shiny = (self.tid ^ h ^ l) < 8 # sid = 0

        self.ivs = get_ivs(rng.rand(), rng.rand())

        self.berry = (rng.rand() // 3) & 1
    
    def __repr__(self):
        return f"Seed: {self.seed:04X} | PID: {self.pid:08X} | Nature: {self.nature:7s} | IVs: {format_ivs(self.ivs)} | Shiny: {self.shiny} | Berry: {JirachiColo.berries[self.berry]}"

class JirachiChannel:
    tid = 40122
    games = ("Ruby", "Sapphire")
    genders = ("Female", "Male")

    def __init__(self, seed=0):
        self.seed = seed & 0xffffffff
        rng = GCRNG(self.seed)

        self.sid = rng.rand()
        
        h = rng.rand()
        l = rng.rand()
        
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

        #self.valid = JirachiChannel.valid_jirachi(self.seed)
    
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

    @staticmethod
    def valid_jirachi(seed):
        pass
    
    def __repr__(self):
        return f"Seed: {self.seed:08X} | PID: {self.pid:08X} | Nature: {self.nature:7s} | IVs: {format_ivs(self.ivs)} | Shiny: {str(self.shiny):5s} | Berry: {JirachiColo.berries[self.berry]:6s} | Game: {JirachiChannel.games[self.game]:8s} | OT Gender: {JirachiChannel.genders[self.ot_gender]}"

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
        rnd = (sid << 16) | (40122 ^ sid)
        
        for s in gcrng_recover_pid_seeds(rnd):
            c += (GCRNG(s).advance(3) >> 16) >= 8 # cannot be shiny in this context
        
        for s in gcrng_recover_pid_seeds(rnd ^ 1):
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