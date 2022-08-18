import sys
sys.path.append(".")
sys.path.append("../")

from RNG import MT, RNGList

def get_pokerus_slot_strain_5(rngList, party):
    slot = (rngList.next() * party) >> 32
    xy = 0
    while (xy & 7) == 0:
        xy = rngList.next() >> 24
    if xy >> 4:
        xy &= 7
    xy |= (xy << 4)
    xy &= 0xf3
    xy += 1
    strain = xy >> 4
    return (slot+1, strain)

if __name__ == "__main__":
    seed = 0x1234567890ABCDEF
    max_advc = 200_000
    party = 6

    mt = MT(seed >> 32)
    rngList = RNGList(mt, 128)

    for advc in range(max_advc):
        if (rngList.next() >> 16) % 0x4000 == 0:
            slot, strain = get_pokerus_slot_strain_5(rngList, party)
            print(f"MT Advances: {advc:{len(str(max_advc))}d} | Slot: {slot} | Strain: {strain}")
        rngList.next_head()