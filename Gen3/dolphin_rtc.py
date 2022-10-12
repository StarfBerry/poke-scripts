### Dolphin Seed to Time ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import GCRNGR, gcrng_recover_pid_seeds
from datetime import datetime, timedelta

def calc_dolphin_seed_distance(s1, s2):
    if (s1 & 0x1f) != (s2 & 0x1f):
        return -1
    diff = (s2 - s1) >> 5
    return (0x4e4069 * diff) & 0x7ffffff

def generate_dolphin_seeds(calibration_seed, target_seed, dt_start, dt_end, min_advc=0, max_advc=10_000):
    rng = GCRNGR(target_seed)
    rng.advance(min_advc)
    low = calibration_seed & 0x1f
    
    res = False
    for advc in range(min_advc+1, max_advc):
        seed = rng.next()
        if (seed & 0x1f) == low:
            dist = calc_dolphin_seed_distance(calibration_seed, seed)
            dt = dt_start + timedelta(seconds=dist)
            if dt < dt_end:
                print(f"Initial Seed: {seed:08X} | Advances: {advc:{len(str(max_advc))}d} | DateTime: {dt}")
                res = True
    
    if not res:
        print("No results.")

def search_dolphin_seeds(calibration_seed, dt_start, dt_end, target_seed, search_for_tidsid, tid, sid, min_advc, max_advc):
    if search_for_tidsid:
        tidsid = (tid << 16) | sid 
        
        seeds = gcrng_recover_pid_seeds(tidsid)
        if len(seeds) == 0:
            print("This IDs combo doesn't exists in GC games.")
            return
        
        target_seed = seeds[0]
    
    generate_dolphin_seeds(calibration_seed, target_seed, dt_start, dt_end, min_advc, max_advc)

if __name__ == "__main__":
    calibration_seed = 0x26acbb6
    dt_start = datetime(2000, 1, 1, 0, 0, 0)
    dt_end = datetime(2000, 6, 1, 0, 0, 0)
    
    target_seed = 0xc0cac01a
    search_for_tidsid = True
    tid = 5
    sid = 60669

    min_advc = 10_000
    max_advc = 15_000

    search_dolphin_seeds(calibration_seed, dt_start, dt_end, target_seed, search_for_tidsid, tid, sid, min_advc, max_advc)