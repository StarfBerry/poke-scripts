import sys
sys.path.append(".")
sys.path.append("../")

from RNG import LCRNGR
from Util import ask_int, valid_year

seed = ask_int("Target Seed: 0x", 16) & 0xffffffff
maxAdvc = ask_int("Max Advances: ") + 1
maxDelay = ask_int("Max Delay [0-65536): ", condition=lambda val: 0 <= val < 65536)
year = ask_int("Year [2000-2099]: ", condition=valid_year)
y = year % 2000
print()

rng = LCRNGR(seed)
for advc in range(1, maxAdvc):
    seed = rng.next()
    hour = (seed >> 16) & 0xff
    delay = ((seed & 0xffff) - y) & 0xffffffff
    if hour < 24 and delay < maxDelay:
        print(f"Initial Seed: {seed:08X} | Delay: {delay:{len(str(maxDelay))}d} | Advances: {advc}")