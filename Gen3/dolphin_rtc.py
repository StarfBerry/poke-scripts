### Dolphin Seed To Time ###

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import GCRNGR, gcrng_recover_lower_16bits_pid
from datetime import datetime, timedelta

'''def search_dolphin_seed(calibration_seed, target_seed, dt_start, max_res):
    res = 0
    seconds = 0
    while res < max_res:
        d = GCRNG.calc_distance(calibration_seed, target_seed)
        if min_advc <= d <= max_advc:
            _dt = dt_start + timedelta(seconds=seconds)
            print(f"Seed: {calibration_seed:08X} | Advances: {d:{len(str(max_advc))}d} | DateTime: {_dt}")
            res += 1
        calibration_seed = (calibration_seed + 40_500_000) & 0xffffffff
        seconds += 1'''

def calc_dolphin_seed_distance(s1, s2):
    if (s1 & 0x1F) != (s2 & 0x1F):
        return -1
    diff = (s2 - s1) >> 5
    return (0x4E4069 * diff) & 0x7ffffff

def search_dolphin_seed(calibration_seed, target_seed, dt_start, dt_end, min_advc=0, max_advc=100_000):
    rng = GCRNGR(target_seed)
    rng.advance(min_advc)
    low = calibration_seed & 0x1F
    for advc in range(min_advc+1, max_advc):
        seed = rng.next()
        if (seed & 0x1F) == low:
            dist = calc_dolphin_seed_distance(calibration_seed, seed)
            dt = dt_start + timedelta(seconds=dist)
            if dt < dt_end:
                print(f"Initial Seed: {seed:08X} | Advances: {advc:{len(str(max_advc))}d} | DateTime: {dt}")

if __name__ == "__main__":
    calibration_seed = 0x26acbb6
    dt_start = datetime(2000, 1, 1, 0, 0, 0)
    dt_end = datetime(2000, 6, 1, 0, 0, 0)
    search_for_tidsid = True

    target_seed = 0xC0CAC01A
    tid = 5
    sid = 60669

    min_advc = 10_000
    max_advc = 15_000

    if search_for_tidsid:
        tidsid = (tid << 16) | sid 
        
        seeds = gcrng_recover_lower_16bits_pid(tidsid)
        if len(seeds) == 0:
            print("This IDs combo doesn't exists in GC games.")
            exit()
        
        target_seed = GCRNGR(seeds[0]).next()

    search_dolphin_seed(calibration_seed, target_seed, dt_start, dt_end, min_advc, max_advc)