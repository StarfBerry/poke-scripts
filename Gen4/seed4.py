import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNGR

def get_seed_4(target_seed, max_advc, max_delay, year):
    rng = LCRNGR(target_seed)
    y = year % 2000
    res = False

    for advc in range(1, max_advc):
        seed = rng.next()
        hour = (seed >> 16) & 0xff
        delay = ((seed & 0xffff) - y) & 0xffffffff

        if hour < 24 and delay < max_delay:
            print(f"Initial Seed: {seed:08X} | Delay: {delay:{len(str(max_delay))}d} | Advances: {advc}")
            res = True
    
    if not res:
        print("No results")

if __name__ == "__main__":
    from Util import u32, u16, ask_int, valid_year

    target_seed = u32(ask_int("Target Seed: 0x", 16))
    max_advc = u16(ask_int("Max Advances: "))
    max_delay = ask_int("Max Delay [0-65536): ", condition=lambda val: 0 <= val < 65536)
    year = ask_int("Year [2000-2099]: ", condition=valid_year)
    print()

    get_seed_4(target_seed, max_advc, max_delay, year)