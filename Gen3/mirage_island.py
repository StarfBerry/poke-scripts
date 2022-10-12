'''
Script to find a static/wild Pokémon with a PID which matches your Mirage Island value.
To check your Mirage Island value: https://projectpokemon.org/home/files/file/2888-pkhex-plugin-mirage-island-tool/
'''

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, LCRNGR

def generate_wild_pid_low(seed, mirage, delay):
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


def generate_static_pid_low(seed, mirage, delay):
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
        generate_wild_pid_low(seed, mirage, delay)
    else:
        generate_static_pid_low(seed, mirage, delay)