import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, LCRNGR, lcrng_recover_lower_16bits_pid
from Util import get_nature, get_hp_type, get_hp_damage, get_ivs, format_ivs
from primality import primality
import primesieve

is_prime = primality.isprime

def pid_seed_to_ivs(pid_seed, method=1):
    rng = LCRNG(pid_seed)
    iv1 = rng.advance(2 + (method == 2), 16)
    iv2 = rng.advance(1 + (method == 4), 16)
    return get_ivs(iv1, iv2)

def prime_ivs(ivs):
    return all(is_prime(iv) for iv in ivs)

def static_wild_prime():
    primes = (0x2, 0x3, 0x5, 0x7, 0xB, 0xD)
    methods = (1, 2, 4)
    fmt = "PID: {:08X} | IVs: {:17s} | Nature: {:7s} {:2d} | HP: {} {} | Method: {} | Seed: {:08X}"
    for i in primes:
        a = i << 28
        for j in primes:
            b = j << 24
            for k in primes:
                c = k << 20
                for l in primes[1:]:
                    d = l << 16
                    for m in primes:
                        e = m << 12
                        for n in primes:
                            f = n << 8
                            for o in primes:
                                g = o << 4
                                for h in primes[1:]:
                                    pid = a | b | c | d | e | f | g | h
                                    if is_prime(pid) and is_prime(pid >> 16) and is_prime(pid & 0xffff) and is_prime(nature := pid % 25):
                                        for seed in lcrng_recover_lower_16bits_pid(pid):
                                            for method in methods:
                                                if prime_ivs(ivs := pid_seed_to_ivs(seed, method)):
                                                    print(fmt.format(pid, format_ivs(ivs), get_nature(pid), nature, get_hp_type(ivs), get_hp_damage(ivs), method, LCRNGR(seed).next()))

def prime_pid():
    prime_bytes = []
    for p in primesieve.primes(2, 256):
        if is_prime(p >> 4) and is_prime(p & 0xf):
            prime_bytes.append(p)
    for a in prime_bytes:
        for b in prime_bytes:
            for c in prime_bytes:
                for d in prime_bytes:
                    pid = (a << 24) | (b << 16) | (c << 8) | d
                    if is_prime(pid) and is_prime(pid >> 16) and is_prime(pid & 0xffff) and is_prime(pid % 25):
                        print(f"{pid:08X}, {get_nature(pid)}, {d}")

if __name__ == "__main__":
    #static_wild_prime()

    '''
    PID: 22752DB5 | IVs: 19.23.29.23.29.13 | Nature: Relaxed  7 | HP: Dark 42 | Method: 1 | Seed: 2C65E94A
    PID: 353B2B27 | IVs: 11.07.19.31.11.23 | Nature: Rash    19 | HP: Dark 70 | Method: 4 | Seed: 18652DEE
    PID: 3DBBD7DB | IVs: 17.23.29.29.05.03 | Nature: Quiet   17 | HP: Dark 36 | Method: 1 | Seed: A958FF15
    PID: D5353DB5 | IVs: 13.13.29.17.31.31 | Nature: Jolly   13 | HP: Dark 55 | Method: 4 | Seed: DAE50EA9
    '''
    prime_pid() # 3DB52B3D, Hasty, 61