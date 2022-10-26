### Script to search for starter Eevee with specific traits in Pokemon XD Gales of Darkness ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import GCRNG, GCRNGR, gcrng_recover_pid_seeds, gcrng_recover_ivs_seeds
from Util import get_nature, get_gender, get_ivs, get_hp_type, get_hp_damage, format_ivs

class EeveeXD:
    abilities = ("Run Away", "Adaptability")
    
    def __init__(self, seed=0):
        self.seed = seed
        rng = GCRNG(seed)

        self.tid = rng.next_u16()
        self.sid = rng.next_u16()

        rng.advance(2)
        
        iv1 = rng.next_u16()
        iv2 = rng.next_u16()
        self.ivs = get_ivs(iv1, iv2)

        self.ability = rng.next_u16() & 1

        pidh = rng.next_u16()
        pidl = rng.next_u16()
        self.pid = (pidh << 16) | pidl

        self.nature = get_nature(self.pid)
        self.gender = self.pid & 0xff
        self.shiny = (self.tid ^ self.sid ^ pidh ^ pidl) < 8
    
    def __repr__(self):
        hp_type = get_hp_type(self.ivs)
        hp_dmge = get_hp_damage(self.ivs)
        ability = EeveeXD.abilities[self.ability]
        gender = get_gender(self.gender, 1/8)
        return f"Seed: {self.seed:08X} | TID/SID: {self.tid:05d}/{self.sid:05d} | IVs: {format_ivs(self.ivs)} | Hidden Power: {hp_type:<8} {hp_dmge:<2} | Ability: {ability:<12} | PID: {self.pid:08X} | Gender: {gender:<6} | Nature: {self.nature:<7} | Shiny: {self.shiny}"

    @staticmethod
    def ivs_to_eevee(hp, atk, dfs, spa, spd, spe):
        seeds = gcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)
        return [EeveeXD(GCRNGR(seed).advance(4)) for seed in seeds]
    
    @staticmethod
    def tidsid_to_eevee(tid, sid):
        tidsid = (tid << 16) | sid
        seeds = gcrng_recover_pid_seeds(tidsid)
        return [EeveeXD(seed) for seed in seeds]

    @staticmethod
    def pid_to_eevee(pid):
        seeds = gcrng_recover_pid_seeds(pid)
        return [EeveeXD(GCRNGR(seed).advance(7)) for seed in seeds]

def search_eevee(min_ivs, max_ivs, search_for_shiny, search_for_nature, target_natures):
    if search_for_shiny:
        if search_for_nature:
            check = lambda eevee: eevee.shiny and eevee.nature in target_natures
        else:
            check = lambda eevee: eevee.shiny
    elif search_for_nature:
        check = lambda eevee: eevee.nature in target_natures
    else:
        check = lambda eevee: True
    
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for eevee in EeveeXD.ivs_to_eevee(hp, atk, dfs, spa, spd, spe):
                                if check(eevee):
                                    print(eevee)

def search_shiny_tid_eevee(tid):
    for sid in range(0x10000):
        test = EeveeXD.tidsid_to_eevee(tid, sid)
        for eevee in test:
            if eevee.shiny:
                print(eevee)

if __name__ == "__main__":
    '''min_ivs = (27, 0, 27, 31, 27, 27)
    max_ivs = (31, 31, 31, 31, 31, 31)
    search_for_shiny = True
    search_for_nature = True
    target_natures = ("Timid", "Modest")
    
    search_eevee(min_ivs, max_ivs, search_for_shiny, search_for_nature, target_natures)'''

    '''test = EeveeXD.pid_to_eevee(0x10101010)
    for eevee in test:
        print(eevee)'''

    search_shiny_tid_eevee(5)