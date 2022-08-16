### Script to hit a specific 16bit low for egg's pid in RS and FRLG games ###

from RNG import LCRNG
from Util import ask_int

seed = ask_int("Initial Seed: 0x", 16)
target_low = ask_int("Target Low [0x1-0xfffe]: 0x", 16, lambda low: 0 < low < 0xffff)
max_advc = ask_int("Max Advances: ") + 1
compatibility = ask_int("Daycare Compatibility (20, 50 or 70) ? ", condition=lambda c: c in (20, 50, 70))
delay = ask_int("Delay: ")
print()

rng = LCRNG(seed)
rng.advance(delay)
res = False

for advc in range(1, max_advc):
    prev = rng.state
    low = (rng.rand() % 0xfffe) + 1
    if low == target_low:
        test = ((prev >> 16) * 100) // 0xffff
        if test < compatibility:
            print(advc)
            res = True

if not res:
    print("no results :(")