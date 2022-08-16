### Dolphin Seed To Time ###

from RNG import GCRNG, GCRNGR, gcrng_recover_lower_16bits_pid, gcrng_recover_lower_16bits_ivs
from datetime import datetime, timedelta

def search_dolphin_seed(calibration_seed, target_seed, dt_start, max_res):
    res = 0
    seconds = 0
    while res < max_res:
        d = GCRNG.calc_distance(calibration_seed, target_seed)
        if min_advc <= d <= max_advc:
            _dt = dt_start + timedelta(seconds=seconds)
            print(f"Seed: {calibration_seed:08X} | Advances: {d:{len(str(max_advc))}d} | DateTime: {_dt}")
            res += 1
        calibration_seed = (calibration_seed + 40_500_000) & 0xffffffff
        seconds += 1

if __name__ == "__main__":
    calibration_seed = 0x26acbb6
    dt_start = datetime(2000, 1, 1, 0, 0, 0)
    search_for_tidsid = False

    target_seed = 0xC0CAC01A
    tid = 10101
    sid = 10101

    min_advc = 30_000
    max_advc = 100_000
    max_results = 5

    if search_for_tidsid:
        tidsid = (tid << 16) | sid 
        
        seeds = gcrng_recover_lower_16bits_pid(tidsid)
        if len(seeds) == 0:
            print("This IDs combo doesn't exists in GC games.")
            exit()
        
        target_seed = GCRNGR(seeds[0]).next()

    search_dolphin_seed(calibration_seed, target_seed, dt_start, max_results)