### Script to recover 16bit initial seed from 32bit target seed ###

from Util import ask_int, u32
from RNG import LCRNGR

def get_init_seed(seed, min_advc, max_advc):
    res = []
    rng = LCRNGR(seed)
    rng.advance(min_advc)
    for advc in range(min_advc+1, max_advc):
        if (state := rng.next()) < 0x10000:
            return (state, advc)
    return (None, -1)

if __name__ == "__main__":
    target_seed = u32(ask_int("Target Seed: 0x", 16))
    min_advc = u32(ask_int("Min Advances: "))
    max_advc = u32(ask_int("Max Advances: "))
    print()

    fmt = "Seed: {:04X} | Advances: {}"

    init = get_init_seed(target_seed, min_advc, max_advc)
    if init[0] is not None:
        print(fmt.format(*init))
    else:
        print("no results :(")