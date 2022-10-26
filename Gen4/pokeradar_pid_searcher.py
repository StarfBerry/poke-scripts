import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNGR, lcrng_recover_ivs_seeds
from Util import get_nature

def search_chained_shiny_pid(pid, min_ivs, max_ivs):
    target_low = pid & 0xffff
    target_high = (pid >> 16) & 7

    res = False
    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
                            for seed in lcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)[0::2]:
                                rng = LCRNGR(seed)

                                low = ((seed >> 16) & 1) << 15
                                for i in range(14, 2, -1):
                                    low |= (rng.next_u16() & 1) << i

                                high = rng.next_u16() & 7
                                low |= rng.next_u16() & 7

                                if low == target_low and high == target_high:
                                    print(f"Seed: {seed:08X}/{seed ^ 0x80000000:08X} | IVs: {[hp, atk, dfs, spa, spd, spe]}")
                                    res = True
    
    if not res:
        print("No results :(")

def search_chained_shiny_pids(pids, min_ivs, max_ivs):
    lows, highs = [], []
    for pid in pids:
        lows.append(pid & 0xffff)
        highs.append((pid >> 16) & 7)

    for hp in range(min_ivs[0], max_ivs[0]+1):
        for atk in range(min_ivs[1], max_ivs[1]+1):
            for dfs in range(min_ivs[2], max_ivs[2]+1):
                for spa in range(min_ivs[3], max_ivs[3]+1):
                    for spd in range(min_ivs[4], max_ivs[4]+1):
                        for spe in range(min_ivs[5], max_ivs[5]+1):
    
                            for seed in lcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe)[0::2]:
                                rng = LCRNGR(seed)

                                low = ((seed >> 16) & 1) << 15
                                for i in range(14, 2, -1):
                                    low |= (rng.next_u16() & 1) << i

                                high = rng.next_u16() & 7
                                low |= rng.next_u16() & 7

                                if low in lows:
                                    index = lows.index(low) 
                                    if high == highs[index]:
                                        pid = pids[index]
                                        print(hex(rng.state), hex(rng.state ^ 0x80000000))
                                        print(f"{pid:08x} {get_nature(pid)}") 
                                        print(hp, atk, dfs, spa, spd, spe)
                                        print("####################")
    

if __name__ == "__main__":
    pids = [
        0x00000000, 0x11111111, 0x22222222, 0x33333333, 0x44444444, 0x55555555, 0x66666666, 0x77777777, 
        0x88888888, 0x99999999, 0xaaaaaaaa, 0xbbbbbbbb, 0xcccccccc, 0xdddddddd, 0xeeeeeeee, 0xffffffff,
        0xdeadbeef, 0xdeadc0de, 0xc0cac01a, 0x10101010, 0x3bd52b3d, 0x00ba0bab, 0x0badface, 0x12345678,
        0x01010101, 0xcafebabe, 0x00decade, 0x8badf00d, 0xba5eba11, 0xf007ba11, 0xfaceb00c, 0x00c1cada,
        0xbaaaaaad, 0xabadbabe, 0x0badc0de, 0xcafed00d, 0xd15ea5ed, 0x00000132, 0xd1770132, 0x132d1770]
    
    pids.extend([int(str(i), 16) for i in range(1, 494)])

    for iv in range(32):
        a = b = [iv] * 6
        search_chained_shiny_pids(pids, a, b)

    max_ivs = [31, 31, 31, 31, 31, 31]

    for min_ivs in ([30, 30, 30, 0, 30, 30], [30, 0, 30, 30, 30, 30], [30, 30, 30, 30, 30, 0]):
        search_chained_shiny_pids(pids, min_ivs, max_ivs)