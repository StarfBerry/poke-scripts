### Script to hit a specific 16bit low for egg's pid in RS and FRLG games ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG

def generate_16bit_low_pid(seed, target_low, max_advc, compatibility, delay):
    rng = LCRNG(seed)
    rng.advance(delay)
    res = False

    for advc in range(1, max_advc):
        prev = rng.state
        low = rng.rand(0xfffe) + 1
        if low == target_low:
            test = ((prev >> 16) * 100) // 0xffff
            if test < compatibility:
                print(advc)
                res = True
    
    if not res:
        print("no results :(")

if __name__ == "__main__":
    from Util import ask_int, u8, u16, u32

    seed = u16(ask_int("Initial Seed: 0x", 16))
    target_low = ask_int("Target Low [0x1-0xfffe]: 0x", 16, lambda low: 0 < low < 0xffff)
    max_advc = u32(ask_int("Max Advances: "))
    compatibility = ask_int("Parents Compatibility (20, 50 or 70) ? ", condition=lambda c: c in (20, 50, 70))
    delay = u8(ask_int("Delay: "))
    print()

    generate_16bit_low_pid(seed, target_low, max_advc, compatibility, delay)