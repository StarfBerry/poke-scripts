'''
Script to get Pokérus at the end of battle in RSE.
To find your delay on emu: https://github.com/DevonStudios/LuaScripts/blob/main/Gen%203/VBA/Side/RS_Pok%C3%A9rus_RNG.lua
'''

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import LCRNG

def get_pokerus_slot_strain_3(seed, party, emerald=True):
    rng = LCRNG(seed)
    slot = party
    while slot >= party:
        slot = rng.rand() % 6
    if emerald:
        check = lambda xy: (xy & 7) == 0
    else:
        check = lambda xy: xy == 0 # Strain 0 only possible in RS
    xy = 0
    while check(xy):
        xy = rng.rand()
    if xy & 0xf0:
        xy &= 7
    xy |= (xy << 4)
    xy &= 0xf3
    xy += 1
    strain = xy >> 4
    return (slot+1, strain)

if __name__ == "__main__":
    from Util import ask_int, ask, u32
    
    game = ask("Emerald ? Y/N: ")
    seed = u32(ask_int("Initial Seed: 0x", 16))
    minAdvc = u32(ask_int("Min Advances: "))
    maxAdvc = u32(ask_int("Max Advances: "))
    party = ask_int("How many mon in your party ? ", condition=lambda val: 0 < val <= 6)
    delay = u32(ask_int("Delay: "))
    
    print("\n| {:9} | {} | {} |".format("Advances", "Party Slot", "Strain"))
    print("-" * 35)
    fmt = "| {:<9} | {:^10} | {:^6} |"

    rng = LCRNG(seed)
    rng.advance(minAdvc + delay)

    for advc in range(minAdvc, maxAdvc+1):
        test = rng.rand()
        if test % 0x4000 == 0 and test:
            slot, strain = get_pokerus_slot_strain_3(rng.state, party, game)
            print(fmt.format(advc, slot, strain))
    
    print("-" * 35)