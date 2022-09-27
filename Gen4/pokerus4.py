''' 
Script to find initial seeds to get pokerus on low advances in Platinum and HGSS.
You have to hit the initial seed then use Sweet Scent on the indicated advances and KO'd the mon you encounter during the first turn.
Make sure you don't have egg in your party at the indicated slot.
'''

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, LCRNGR
from datetime import datetime
from Util import get_base_seed

def get_occidentary(seed, advc, hgss=True):
    occ = advc
    rng = LCRNG(seed)
    rnd = rng.rand()
    nat = rnd % 25 if hgss else rnd // 0xA3E
    while 1:
        pid = rng.rand() | (rng.next() & 0xffff0000)
        occ += 2 
        if pid % 25 == nat:
            break
    return occ + 6

def occidentary_to_advances(state, occ, hgss=True):    
    if hgss:
        get_nat = lambda rnd: rnd % 25 # Method K
    else:
        get_nat = lambda rnd: rnd // 0xA3E # Method J
    
    advc = None
    occ -= 6
    rng = LCRNGR(state)
    rng.advance(3)
    h, l = rng.rand(), rng.rand()
    pid = (h << 16) | l
    nat = pid % 25

    while occ >= 2:
        occ -= 2
        h = rng.rand()
        fixed_nat = get_nat(h)
        if fixed_nat == nat:
            advc = occ # no break to get the lowest advc
        
        _pid = (h << 16) | rng.rand()
        if (_pid % 25) == nat: 
            break
    
    return advc

def get_pokerus_slot_strain_4(seed, party):
    rng = LCRNG(seed)
    slot = rng.rand() % party
    xy = 0
    while (xy & 7) == 0:
        xy = rng.rand()
    if xy & 0xf0:
        xy &= 7
    xy |= (xy << 4)
    xy &= 0xf3
    xy += 1
    strain = xy >> 4
    return (slot+1, strain)

def search_pkrs_4(dt, hgss, party, min_delay, max_delay, max_advc):
    fmt = "Init Seed: {:08X} | Advances: {:3d} -> Occidentary: {:3d} | Slot: {} | Strain: {:2d} | Delay: {}"
    
    max_occ = max_advc * 2
    base_seed = get_base_seed(dt)
    for delay in range(min_delay, max_delay, 2):
        seed = (base_seed + delay) & 0xffffffff
        rng = LCRNG(seed)
        rng.next() # to make a difference of 2 between advc and occ
        for occ in range(max_occ):
            test = rng.rand()
            if (test % 0x4000) == 0 and test:
                advc = occidentary_to_advances(LCRNGR(rng.state).advance(2), occ, hgss)
                if advc is not None and advc <= max_advc:
                    slot, strain = get_pokerus_slot_strain_4(rng.state, party)
                    print(fmt.format(seed, advc, occ, slot, strain, delay))

if __name__ == "__main__":
    dt = datetime(2022, 2, 22, 22, 22, 22)
    hgss = False
    party = 2
    min_delay = 800
    max_delay = 2000
    max_advc = 200

    search_pkrs_4(dt, hgss, party, min_delay, max_delay, max_advc)