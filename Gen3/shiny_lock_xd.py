import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import GCRNG, gcrng_recover_ivs_seeds
from Util import get_psv, get_nature, get_hp_type, get_hp_damage, get_psv, format_ivs

def generate_anti_shiny_spread(min_ivs, max_ivs, natures):
    fmt = "Seed: {:08X} | PID: {:08X} {:9s} -> {:08X} {:9s} | PSV: {:04d} | IVs: {} | HP: {} {}"
    
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for seed in gcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
                                rng = GCRNG(seed)
                                rng.advance(3)
                                init_pid = (rng.next() & 0xffff0000) | rng.next_u16()
                                pid = init_pid
                                psv = get_psv(pid)
                                while get_psv(pid) == psv:
                                    pid = (rng.next() & 0xffff0000) | rng.next_u16()
                                nat = get_nature(pid)
                                if nat in natures:
                                    psv = get_psv(init_pid)
                                    ivs = (hp, atk, dfs, spa, spd, spe)
                                    init_nat = get_nature(init_pid)
                                    print(fmt.format(seed, init_pid, f"({init_nat})", pid, f"({nat})", psv, format_ivs(ivs), get_hp_type(ivs), get_hp_damage(ivs)))

if __name__ == "__main__":
    min_ivs = (31, 0, 31, 0, 31, 31)
    max_ivs = (31, 0, 31, 31, 31, 31)
    natures = ("Bold")

    generate_anti_shiny_spread(min_ivs, max_ivs, natures)