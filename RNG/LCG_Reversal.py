def reverse_lcg(mul, add):
    rmul = pow(mul, -1, m := 1 << 32)
    radd = (-rmul * add) % m
    return (rmul, radd)

def reverse_lcg_64(mul, add):
    rmul = pow(mul, -1, m := 1 << 64)
    radd = (-rmul * add) % m
    return (rmul, radd)

def lcrng_prev(s):
    return (s * 0xEEB9EB65 + 0x0A3561A1) & 0xffffffff

def gcrng_prev(s):
    return (s * 0xB9B33155 + 0xA170F641) & 0xffffffff

######################################################################

LCRNG_MUL   = 0x41C64E6D # LCRNG mul constant
LCRNG_ADD   = 0x6073     # LCRNG add constant
LCRNG_MOD   = 0x67D3     # u32(0x67d3 * LCRNG_MUL) < 2^16 (for seed and seed + 0x67d3, we have a good chance that the 16bit high of the next output will be the same for both)
LCRNG_PAT   = 0xD3E      # pattern in the distribution of the "low solutions" modulo 0x67d3
LCRNG_INC   = 0x4034     # (((diff * 0x67d3 + 0x4034) >> 16) * 0xd3e) % 0x67d3 line up with the first 16bit low solution modulo 0x67d3 if it exists (see diff definition in code)

LCRNG_MUL_2 = 0xC2A29A69 # LCRNG_MUL^2
LCRNG_ADD_2 = 0xE97E7B6A # LCRNG_ADD * (1 + LCRNG_MUL)
LCRNG_MOD_2 = 0x3A89     # u32(0x3a89 * LCRNG_MUL_2) < 2^16 (for seed and seed + 0x3a89, we have a good chance that the 16bit high of the next output will be the same for both)
LCRNG_PAT_2 = 0x2E4C     # pattern in the distribution of the "low solutions" modulo 0x3a89
LCRNG_INC_2 = 0x5831     # (((diff * 0x3a89 + 0x5831) >> 16) * 0x2e4c) % 0x3a89 line up with the first 16bit low solution modulo 0x3a89 if it exists (see diff definition in code)

def lcrng_recover_pid_seeds(pid):
    first = (pid & 0xffff) << 16
    second = pid & 0xffff0000

    diff = ((second - first * LCRNG_MUL) >> 16) & 0xffff
    start = (((diff * LCRNG_MOD + LCRNG_INC) >> 16) * LCRNG_PAT) % LCRNG_MOD

    seeds = []
    for low in range(start, 0x10000, LCRNG_MOD): # at most 3 iterations
        if ((test := first | low) * LCRNG_MUL + LCRNG_ADD) & 0xffff0000 == second:
            seeds.append(lcrng_prev(test))
    
    return seeds

def lcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
    first = (hp | (atk << 5) | (dfs << 10)) << 16
    second = (spe | (spa << 5) | (spd << 10)) << 16
    
    diff = ((second - first * LCRNG_MUL) >> 16) & 0xffff
    start1 = (((diff * LCRNG_MOD + LCRNG_INC) >> 16) * LCRNG_PAT) % LCRNG_MOD
    start2 = ((((diff ^ 0x8000) * LCRNG_MOD + LCRNG_INC) >> 16) * LCRNG_PAT) % LCRNG_MOD

    seeds = []
    for start in (start1, start2):
        for low in range(start, 0x10000, LCRNG_MOD): # at most 3 iterations 
            if ((test := first | low) * LCRNG_MUL + LCRNG_ADD) & 0x7fff0000 == second:
                seeds.append(seed := lcrng_prev(test))
                seeds.append(seed ^ 0x80000000)

    return seeds

# Method 3 PID
def lcrng_recover_pid_seeds_2(pid):
    first = (pid & 0xffff) << 16
    second = pid & 0xffff0000

    diff = ((second - (first * LCRNG_MUL_2 + LCRNG_ADD_2)) >> 16) & 0xffff
    start = (((diff * LCRNG_MOD_2 + LCRNG_INC_2) >> 16) * LCRNG_PAT_2) % LCRNG_MOD_2

    seeds = []
    for low in range(start, 0x10000, LCRNG_MOD_2): # at most 5 iterations
        if ((test := first | low) * LCRNG_MUL_2 + LCRNG_ADD_2) & 0xffff0000 == second:
            seeds.append(lcrng_prev(test))
    
    return seeds

# Method 4 IVs
def lcrng_recover_ivs_seeds_2(hp, atk, dfs, spa, spd, spe):
    first = (hp | (atk << 5) | (dfs << 10)) << 16
    second = (spe | (spa << 5) | (spd << 10)) << 16
    
    diff = ((second - (first * LCRNG_MUL_2 + LCRNG_ADD_2)) >> 16) & 0xffff
    start1 = (((diff * LCRNG_MOD_2 + LCRNG_INC_2) >> 16) * LCRNG_PAT_2) % LCRNG_MOD_2
    start2 = ((((diff ^ 0x8000) * LCRNG_MOD_2 + LCRNG_INC_2) >> 16) * LCRNG_PAT_2) % LCRNG_MOD_2

    seeds = []
    for start in (start1, start2):
        for low in range(start, 0x10000, LCRNG_MOD_2): # at most 5 iterations
            if ((test := first | low) * LCRNG_MUL_2 + LCRNG_ADD_2) & 0x7fff0000 == second:
                seeds.append(seed := lcrng_prev(test))
                seeds.append(seed ^ 0x80000000)

    return seeds

######################################################################

# Reference: https://crypto.stackexchange.com/questions/10608/how-to-attack-a-fixed-lcg-with-partial-output/10629#10629

GCRNG_MUL     = 0x343FD           # GCRNG mul constant
GCRNG_ADD     = 0x269EC3          # GCRNG add constant
GCRNG_SUB     = 0x259EC4          # GCRNG_ADD - 0xffff
GCRNG_BASE    = 0x343FABC02       # (GCRNG_MUL + 1) * 0xffff

# GCRNG_MUL^3 don't produce the lowest KMAX but allows to skip more K's and obtain the fewest iterations for CHANNEL ivs
GCRNG_MUL_3   = 0x45C82BE5        # GCRNG_MUL^3
GCRNG_SUB_3   = 0xCAF65B56        # GCRNG_ADD * (1 + GCRNG_MUL + GCRNG_MUL^2) - 0x7ffffff
GCRNG_BASE_3  = 0x22E415EEA37D41A # (GCRNG_MUL_3 + 1) * 0x7ffffff
GCRNG_PRIME_3 = 0x3               # (3 << 32) % GCRNG_MUL_3 = 0x661D29 (small compared to GCRNG_MUL_3, allow to avoid most values of K that do not pass the test)
GCRNG_ADD_3   = 0x300000000       # 3 << 32
GCRNG_SKIP_3  = 0x661D29          # GCRNG_ADD_3 % GCRNG_MUL_3
GCRNG_RMAX_3  = 0x18000000        # 3 << 27
GCRNG_RADD_3  = 0x132577B         # 3 * GCSKIP_SKIP_3

def gcrng_recover_pid_seeds(pid):
    first = pid & 0xffff0000
    second = (pid & 0xffff) << 16

    t = (second - GCRNG_MUL * first - GCRNG_SUB) & 0xffffffff
    kmax = (GCRNG_BASE - t) >> 32

    seeds = []
    for _ in range(kmax+1): # at most 4 iterations
        if (t % GCRNG_MUL) < 0x10000:
            seeds.append(gcrng_prev(first | (t // GCRNG_MUL)))
        
        t += 0x100000000
        
    return seeds

def gcrng_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
    first = (hp | (atk << 5) | (dfs << 10)) << 16
    second = (spe | (spa << 5) | (spd << 10)) << 16

    t = (second - GCRNG_MUL * first - GCRNG_SUB) & 0x7fffffff
    kmax = (GCRNG_BASE - t) >> 31

    seeds = []
    for _ in range(kmax+1): # at most 7 iterations
        if (t % GCRNG_MUL) < 0x10000:
            seeds.append(seed := gcrng_prev(first | (t // GCRNG_MUL)))
            seeds.append(seed ^ 0x80000000)
        
        t += 0x80000000
        
    return seeds

def channel_recover_ivs_seeds(hp, atk, dfs, spa, spd, spe):
    first = hp << 27

    k = 0
    t = ((spe << 27) - GCRNG_MUL_3 * first - GCRNG_SUB_3) & 0xffffffff
    x = (t * GCRNG_PRIME_3) % GCRNG_MUL_3
    kmax = (GCRNG_BASE_3 - t) >> 32  

    seeds = []
    while k <= kmax: # kmax / (20 * 3 + 115) ~= 209 130 iterations (~ 2^22 tests)
        r = (x + GCRNG_SKIP_3 * k) % GCRNG_MUL_3
        if m := -r % GCRNG_PRIME_3: 
            r += m * GCRNG_SKIP_3 # to make r divisible by 3 (GCRNG_SKIP_3 % 3 == 1)
            k += m
        
        tmp = t + 0x100000000 * k

        while r < GCRNG_RMAX_3 and k <= kmax: # GCRNG_RMAX_3 / GCRNG_RADD_3 = 20
            s = first | (tmp // GCRNG_MUL_3)

            test = (s * GCRNG_MUL + GCRNG_ADD) & 0xffffffff
            if (test >> 27) == atk:
                test = (test * GCRNG_MUL + GCRNG_ADD) & 0xffffffff
                if (test >> 27) == dfs:
                    test = (test * 0xA9FC6809 + 0x1E278E7A) & 0xffffffff # jump on the speed iv since we know he matches
                    if (test >> 27) == spa:
                        test = (test * GCRNG_MUL + GCRNG_ADD) & 0xffffffff
                        if (test >> 27) == spd:
                            seeds.append(s)

            r += GCRNG_RADD_3 # to keep r divisible by 3 
            k += GCRNG_PRIME_3
            tmp += GCRNG_ADD_3

        k += ((GCRNG_MUL_3 - r) + GCRNG_SKIP_3 - 1) // GCRNG_SKIP_3 # ceil((GCRNG_MUL_3 - GCRNG_RMAX_3) / GCRNG_SKIP_3) = 115

    return seeds

######################################################################

def _gcrng_recover_pid_seeds(pid):
    first = pid & 0xffff0000
    second = (pid & 0xffff) << 16

    t = (second - GCRNG_MUL * first - GCRNG_SUB) & 0xffffffff
    kmax = (GCRNG_BASE - t) >> 32

    seeds = []
    for k in range(kmax+1): # at most 4 iterations
        if (t % GCRNG_MUL) < 0x10000:
            seeds.append(first | (t // GCRNG_MUL))
        
        t += 0x100000000
        
    return seeds

def channel_ivs_test(hp, atk, dfs, spa, spd, spe):
    val = (hp << 27) | (atk << 11)

    seeds = []
    for a in range(0x800):
        for b in range(0x800):
            for seed in _gcrng_recover_pid_seeds(val | (a << 16) | b):
                test = (seed * 0xA9FC6809 + 0x1E278E7A) & 0xffffffff # advance of 2 states to check def iv
                if (test >> 27) == dfs:
                    test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                    if (test >> 27) == spe:
                        test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                        if (test >> 27) == spa:
                            test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                            if (test >> 27) == spd:
                                seeds.append(seed)

    return seeds