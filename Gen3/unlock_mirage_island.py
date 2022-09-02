'''
Script to find a static/wild Pokémon with a PID which matches your Mirage Island seed.
To check your Mirage Island seed: https://projectpokemon.org/home/files/file/2888-pkhex-plugin-mirage-island-tool/
'''

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import LCRNG, LCRNGR

def search_wild_16bit_low_pid(seed, mirage, delay):
    rng = LCRNG(seed)
    rng.advance(delay)
    res = False

    for advc in range(max_advc):
        low = rng.rand()
        if low == mirage:
            high = LCRNG(rng.state).rand()
            pid = (high << 16) | low
            nat = pid % 25

            a = advc
            tmp = LCRNGR(rng.state)
            while 1:
                fixed_nat = LCRNGR(tmp.state).rand() % 25
                if fixed_nat == nat:
                    esv = (LCRNGR(tmp.state).advance(3) >> 16) % 100
                    print(f"Advances: {a-4:{len(str(max_advc))}d} | PID: {pid:08X} | ESV: {esv}")
                    res = True
                
                a -= 2
                _pid = (tmp.rand() << 16) | tmp.rand()
                if (_pid % 25) == nat or a < 4: 
                    break
    
    if not res:
        print("No results.")


def search_static_16bit_low_pid(seed, mirage, delay):
    rng = LCRNG(seed)
    rng.advance(delay)
    res = False
    
    for advc in range(max_advc):
        low = rng.rand()
        if low == mirage:
            high = LCRNG(rng.state).rand()
            pid = (high << 16) | low
            print(f"Advances: {advc:{len(str(max_advc))}d} | PID: {pid:08X}")
            res = True
    
    if not res:
        print("No results.")

if __name__ == "__main__":
    from Util import u16, u32, ask_int, ask

    seed = u16(ask_int("Initial Seed: 0x", 16))
    mirage = u16(ask_int("Mirage Island Value: 0x", 16))
    max_advc = u32(ask_int("Max Advances: "))
    wild = ask("Wild encounter ? Y/N: ")
    delay = u16(ask_int("Delay: "))

    print()

    if wild:
        search_wild_16bit_low_pid(seed, mirage, delay)
    else:
        search_static_16bit_low_pid(seed, mirage, delay)