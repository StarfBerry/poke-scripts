### Prototype to check a seed for a full shiny horde in Gen 6 games with recursive approach ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import MT
from Util import get_psv, Pokemon

class Horde5:
    conditions = {
        8: [7],
        9: [5, 6, 7],
        10: [2, 4, 5, 6, 7],
        11: [0, 2, 4, 5, 6, 7],
        12: [0, 2, 4],
        13: [0]
    }
    
    def __init__(self, seed, advc=100_000, delay=0):
        self.seed = seed
        self.advances = advc
        self.delay = delay
    
        mt = MT(self.seed)
        mt.advance(62+delay)
        self.psvs = [get_psv(mt.next(), 4) for _ in range(self.advances+52)]

    def check(self):
        self.results = []
        for advc in range(self.advances):
            self.psv = self.psvs[advc]
            for i in range(8, 14): # possible jumps, assuming the user has shiny charm
                if self.psvs[advc+i] == self.psv:
                    self.advc = advc
                    for j in Horde5.conditions[i]:
                        self.sync, ha, self.gender = j >> 2, (j >> 1) & 1, j & 1
                        self.p = self.sync + self.gender
                        self.min_jump = 11 - self.p
                        self.max_jump = 14 - self.p
                        self.check_full_shiny_horde(advc+i, ha=ha)
        
    def check_full_shiny_horde(self, advc, shiny=2, ha=0, ha_slot=None):
        if ha and ha_slot is None: 
            ha_slot = shiny-1
        if shiny == 5: 
            return (self.advc, self.psv, self.sync != 0, self.gender != 0, ha_slot)
        for i in range(self.min_jump-(not ha), self.max_jump):
            if self.psvs[advc+i] == self.psv:
                test = self.check_full_shiny_horde(advc+i, shiny+1, ha or i == (10-self.p), ha_slot)
                if test is not None: 
                    advc, psv, sync, gender, ha_slot = test
                    horde = Horde5.generate_horde(self.seed, advc, self.delay, sync, ha_slot, gender, psv)
                    if sync != gender: # sync or fixed gender give same advancement
                        sync, gender = "True/False", "False/True"
                    print(f"Seed: {self.seed:08X} | Advances: {advc} | TSV: {psv:4d} | Sync: {str(sync):^10} | HA: {str(ha_slot):^4} | Fixed Gender: {gender}\n")
                    for pkm in horde:
                        print(pkm)
                    print("\n############################################\n")
                    return # don't check for close full shiny hordes
        return None

    @staticmethod
    def generate_horde(seed, advc, delay, sync=False, ha_slot=None, gender_restriction=False, tsv=0): # ignoring fixed ivs and carbink case
        mt = MT(seed)
        mt.advance(61 + advc + delay)
        
        horde = []
        for slot in range(1, 6):
            ec = mt.next()
    
            for _ in range(3):
                pid = mt.next()
                if get_psv(pid, 4) == tsv:
                    break
        
            ivs = [mt.next() >> 27 for _ in range(6)]
            ability = mt.next() >> 31 if slot != ha_slot else 'H'
            nature = mt.rand(25) if not sync else -1
            gender = mt.rand(252) if not gender_restriction else "Fixed"
            
            pkmn = Pokemon(gen=6, ec=ec, pid=pid, ivs=ivs, ability=ability, nature=nature, gender=gender)
            horde.append(pkmn)
        
        return horde

if __name__ == "__main__":
    seeds = [0x002151bd, 0x089120f4, 0xd8839825] 
    
    advances = 100_000
    delay = 174

    test = Horde5(seeds[0], advances, delay)
    test.check()

''' 
Note for later:
- The number of rand calls for fixed ivs is not constant so it's possible to have jumps greater than 13.
- And a "regular" shiny horde will not always work with a Mime Jr./Smoochum horde (3 fixed ivs caused by their unknown egg group).
- We need to track how many rand calls has been done for fixed ivs in this case.
'''