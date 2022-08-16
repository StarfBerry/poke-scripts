### Script to generate a couple of prime IDs to make a pid to be shiny if possible ###

from primesieve import nth_prime, primes
from primality import primality
from random import randint
from Util import ask, ask_int
from RNG import lcrng_recover_lower_16bits_pid, gcrng_recover_lower_16bits_pid

is_prime = primality.isprime

def print_ids(tid, sid, pxor, gen):
    out = f"TID: {tid:05d} | SID: {sid:05d} |"
    if gen == 3:
        tidsid = (tid << 16) | sid
        out += f" tidsid: {tidsid:08X} |"
    elif gen == 4:
        pass
    elif gen >= 7:
        g7id = (tid + sid * 0x10000) % 10**6
        out += f" G7ID: {g7id:06d} |"
    xor = tid ^ sid ^ pxor
    shiny = "Star" if xor else "Square"
    out += f" Shiny: {shiny} (XOR={xor})"
    print(out)

def valid_result(tid, sid, gen, rs, gc, wild5, pid_bit):
    if rs or gc:
        tidsid = (tid << 16) | sid
        seeds = gcrng_recover_lower_16bits_pid(tidsid) if gc else lcrng_recover_lower_16bits_pid(tidsid)
        return len(seeds) != 0 # tid/sid combo exists
    # cannot check effectively if tid/sid is possible in Gen 4
    elif wild5:
        return pid_bit == ((tid & 1) ^ (sid & 1)) # pid_bit == id_bit to follow the rule (HPID ^ LPID ^ LTID ^ LSID) == 0
    elif gen > 6:
        return is_prime((tid + sid * 0x10000) % 10**6) # tid, sid and G7 id must be prime. G7 id has around 8% chance to be prime.
    return True

def prime_ids_generator(pid, gen, square, rs, gc, wild5, custom_tid=None):
    x = 0 if square else 7 if gen < 6 else 15
    pxor = (pid >> 16) ^ (pid & 0xffff)
    pid_bit = (pid >> 31) ^ (pid & 1)
    mask = 0xffff - x
    res = False

    if custom_tid:
        low_sid = (custom_tid ^ pxor) & mask
        for sid in primes(low_sid, low_sid + x):
            if valid_result(custom_tid, sid, gen, rs, gc, wild5, pid_bit):
                print_ids(custom_tid, sid, pxor, gen)
                res = True
        if not res:
            print(f"No resuts with TID {custom_tid} :(")
    elif (square and (pxor & 1) == 1) or (wild5 and pid_bit == 1): # ids have different parity -> try with sid = 2
        low_tid = (pxor ^ 2) & mask
        tids = primes(low_tid, low_tid + x)
        for tid in tids:
            if valid_result(tid, 2, gen, rs, gc, wild5, pid_bit):
                print_ids(tid, 2, pxor, gen)
                res = True
        if not res:
            shiny = "square shiny" if square else "shiny"
            if wild5: 
                gen = "5 for Wild/Static"
            print(f"Prime IDs + {shiny} is impossible with PID {pid:08X}{f' in Gen {gen}' if (wild5 or len(tids)) else ''}.")
    else:
        while not res:
            tid = nth_prime(randint(1, 6542)) # there are 6542 prime numbers less than 65536
            low_sid = (tid ^ pxor) & mask
            for sid in primes(low_sid, low_sid + x):
                if valid_result(tid, sid, gen, rs, gc, wild5, pid_bit):
                    print_ids(tid, sid, pxor, gen)
                    res = True

if __name__ == "__main__":
    pid = ask_int("PID: 0x", 16) & 0xffffffff
    gen = ask_int("What Gen ? ")
    rs = gen == 3 and ask("RS ? Y/N: ")
    gc = gen == 3 and not rs and ask("GameCube ? Y/N: ")
    wild5 = gen == 5 and ask("Wild/Static ? Y/N: ")
    custom_tid = ask("Custom Prime TID ? Y/N: ") and ask_int("TID: ", condition=lambda tid: is_prime(tid) and 2 <= tid <= 65521)
    square = ask("Square only ? Y/N: ")
    print()
    prime_ids_generator(pid, gen, square, rs, gc, wild5, custom_tid)  