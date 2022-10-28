### Script to generate a couple of prime IDs to make a pid to be shiny if possible ###

from primesieve import nth_prime, primes
from random import randint
from RNG import lcrng_recover_pid_seeds, gcrng_recover_pid_seeds

def is_prime(x):
    if x < 4: 
        return x >= 2
    if x % 2 == 0 or x % 3 == 0: 
        return False
    return all(x % i and x % (i + 2) for i in range(5, int(x**.5) + 1, 6))
    
def print_ids(tid, sid, pxor, gen):
    out = f"TID: {tid:05d} | SID: {sid:05d} |"
    if gen == 3:
        tidsid = (tid << 16) | sid
        out += f" tidsid: {tidsid:08X} |"
    elif gen >= 7:
        g7id = (tid + sid * 0x10000) % 10**6
        out += f" G7ID+: {g7id:06d} |"
    xor = tid ^ sid ^ pxor
    shiny = "Star" if xor else "Square"
    out += f" Shiny: {shiny} (XOR={xor})"
    print(out)

def generate_prime_ids(pid, gen, square, rs, gc, wild5, custom_tid):
    x = 0 if square else 7 if gen < 6 else 15
    pxor = (pid >> 16) ^ (pid & 0xffff)
    mask = 0xffff - x
    res = False

    if rs:
        check = lambda tid, sid: len(lcrng_recover_pid_seeds((tid << 16) | sid)) != 0
    elif gc:
        check = lambda tid, sid: len(gcrng_recover_pid_seeds((tid << 16) | sid)) != 0
    elif wild5:
        pid_bit = (pid >> 31) ^ (pid & 1)
        check = lambda tid, sid: ((tid & 1) ^ (sid & 1)) == pid_bit # id_bit == pid_bit to follow the rule (HPID ^ LPID ^ LTID ^ LSID) == 0
    elif gen >= 7:
        check = lambda tid, sid: is_prime((tid + sid * 0x10000) % 10**6) # tid, sid and G7ID+ must be prime. G7ID+ has around 8% chance to be prime.
    else:
        check = lambda tid, sid: True

    if custom_tid:
        low_sid = (custom_tid ^ pxor) & mask
        for sid in primes(low_sid, low_sid + x):
            if check(custom_tid, sid):
                print_ids(custom_tid, sid, pxor, gen)
                res = True
        if not res:
            print(f"No results with TID {custom_tid:05d} :(")
    elif (square and pxor & 1) or (wild5 and pid_bit): # ids have different parity ==> try with sid = 2
        sid = 2
        low_tid = (pxor ^ sid) & mask
        tids = primes(low_tid, low_tid + x)
        for tid in tids:
            if check(tid, sid):
                print_ids(tid, sid, pxor, gen)
                res = True
        if not res:
            shiny = "square shiny" if square else "shiny"
            if wild5: 
                gen = "5 at least for Wild/Static"
            print(f"Prime IDs + {shiny} is impossible with PID {pid:08X}{f' in Gen {gen}' if (wild5 or len(tids) != 0) else ''}.")
    else:
        while not res:
            tid = nth_prime(randint(1, 6542)) # there are 6542 prime numbers < 65536
            low_sid = (tid ^ pxor) & mask
            for sid in primes(low_sid, low_sid + x):
                if check(tid, sid):
                    print_ids(tid, sid, pxor, gen)
                    res = True

if __name__ == "__main__":
    from Util import ask, ask_int, u32

    pid = u32(ask_int("PID: 0x", 16))
    gen = ask_int("What Gen ? ")
    rs = gen == 3 and ask("RS ? Y/N: ")
    gc = gen == 3 and not rs and ask("GameCube ? Y/N: ")
    wild5 = gen == 5 and ask("Wild/Static ? Y/N: ")
    custom_tid = ask("Custom Prime TID ? Y/N: ") and ask_int("TID: ", condition=lambda tid: tid < 65536 and is_prime(tid))
    square = ask("Square only ? Y/N: ")
    
    print()
    
    generate_prime_ids(pid, gen, square, rs, gc, wild5, custom_tid)