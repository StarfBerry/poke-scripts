from math import ceil

# For the math behind this, refer to https://crypto.stackexchange.com/questions/10608/how-to-attack-a-fixed-lcg-with-partial-output/10629#10629
# PRIME and SKIP constants are used to avoid most values of K that do not pass the test.

GCRNG_MUL      = 0x343FD          # GCRNG mul constant     
GCRNG_SUB      = 0x259EC4         # GCRNG add - 0xFFFF
GCRNG_BASE     = 0x343FABC02      # (GCRNG_MUL + 1) * 0xFFFF

LCRNG_MUL      = 0x41C64E6D       # LCRNG mul constant   
LCRNG_SUB      = 0xFFFF6074       # (LCRNG add - 0xFFFF) & 0xFFFFFFFF
LCRNG_BASE     = 0x41C60CA7B192   # (LCRNG_MUL + 1) * 0xFFFF
LCRNG_PRIME    = 0x25
LCRNG_RMAX     = 0x250000
LCRNG_SKIP1    = 0x73E2B0
LCRNG_SKIP2    = 0x39F158 

# LCRNGR give better skips than LCRNG for Method 2
LCRNGR_MUL_2   = 0xDC6C95D9        # 0xEEB9EB65^2 & 0xFFFFFFFF
LCRNGR_SUB_2   = 0x4D3BB127        # (0xA3561A1^2 - 0xFFFF) & 0xFFFFFFFF
LCRNGR_BASE_2  = 0xDC6BB96D6A26    # (LCRNGR_MUL_2 + 1) * 0xFFFF
LCRNGR_PRIME_2 = 0x1F
LCRNGR_RMAX_2  = 0x1F0000
LCRNGR_SKIP1_2 = 0xBAED7C
LCRNGR_SKIP2_2 = 0x5D76BE

# GCRNG_MUL^3 don't produce the lowest KMAX but allow to skip more K's and obtain the least iterations for CHANNEL ivs
GCRNG_MUL_3   = 0x45C82BE5        # GCRNG_MUL^3 & 0xFFFFFFFF
GCRNG_SUB_3   = 0xCAF65B56        # (0x269EC3 * sum(GCRNG_MUL**i for i in range(3)) - 0xFFFF) & 0xFFFFFFFF
GCRNG_BASE_3  = 0x22E415EEA37D41A # (GCRNG_MUL_3 + 1) * 0x7FFFFFF
GCRNG_PRIME_3 = 0x3
GCRNG_ADD_3   = 0x300000000
GCRNG_RMAX_3  = 0x18000000
GCRNG_SKIP_3  = 0x661D29

def gcrng_recover_lower_16bits_pid(pid):
    first = pid & 0xffff0000
    second = (pid & 0xffff) << 16

    t = (second - GCRNG_MUL * first - GCRNG_SUB) & 0xffffffff
    kmax = (GCRNG_BASE - t) >> 32

    res = []
    for k in range(kmax+1): # at most 4 iterations
        if (t % GCRNG_MUL) < 0x10000:
            res.append(first | (t // GCRNG_MUL))
        
        t += 0x100000000
        
    return res

def gcrng_recover_lower_16bits_ivs(hp, atk, dfs, spa, spd, spe):
    first = (hp | (atk << 5) | (dfs << 10)) << 16
    second = (spe | (spa << 5) | (spd << 10)) << 16

    t = (second - GCRNG_MUL * first - GCRNG_SUB) & 0x7fffffff
    kmax = (GCRNG_BASE - t) >> 31

    res = []
    for k in range(kmax+1): # at most 7 iterations
        if (t % GCRNG_MUL) < 0x10000:
            s = first | (t // GCRNG_MUL)
            res.extend((s, s ^ 0x80000000))
        
        t += 0x80000000
        
    return res

def lcrng_recover_lower_16bits_pid(pid):
    first = (pid & 0xffff) << 16 
    second = pid & 0xffff0000
    
    k = 0
    t = (second - LCRNG_MUL * first - LCRNG_SUB) & 0xffffffff
    x = (t * LCRNG_PRIME) % LCRNG_MUL
    kmax = (LCRNG_BASE - t) >> 32
    
    res = []
    while k <= kmax: # at most 117 iterations
        r = (x + LCRNG_SKIP1 * k) % LCRNG_MUL
        if r % LCRNG_PRIME == 0 and r < LCRNG_RMAX:
            tmp = t + k * 0x100000000
            res.append(first | (tmp // LCRNG_MUL))
        
        k += ceil((LCRNG_MUL - r) / LCRNG_SKIP1)
    
    return res

def lcrng_recover_lower_16bits_ivs(hp, atk, dfs, spa, spd, spe):
    first = (hp | (atk << 5) | (dfs << 10)) << 16
    second = (spe | (spa << 5) | (spd << 10)) << 16

    k = 0
    t = (second - LCRNG_MUL * first - LCRNG_SUB) & 0x7fffffff
    x = (t * LCRNG_PRIME) % LCRNG_MUL
    kmax = (LCRNG_BASE - t) >> 31

    res = []
    while k <= kmax: # at most 117 iterations
        r = (x + LCRNG_SKIP2 * k) % LCRNG_MUL
        if r % LCRNG_PRIME == 0 and r < LCRNG_RMAX:
            tmp = t + k * 0x80000000
            s = first | (tmp // LCRNG_MUL)
            res.extend((s, s ^ 0x80000000))

        k += ceil((LCRNG_MUL - r) / LCRNG_SKIP2)

    return res

def lcrng_recover_lower_16bits_pid_2(pid):
    first = pid & 0xffff0000
    second = (pid & 0xffff) << 16 
    
    k = 0
    t = (second - LCRNGR_MUL_2 * first - LCRNGR_SUB_2) & 0xffffffff
    x = (t * LCRNGR_PRIME_2) % LCRNGR_MUL_2
    kmax = (LCRNGR_BASE_2 - t) >> 32
    
    res = []
    while k <= kmax: # at most 188 iterations
        r = (x + LCRNGR_SKIP1_2 * k) % LCRNGR_MUL_2
        if r % LCRNGR_PRIME_2 == 0 and r < LCRNGR_RMAX_2:
            tmp = t + k * 0x100000000
            low = ((tmp // LCRNGR_MUL_2) * 0x95D9 + 0xB126) & 0xffff # backward of 2 states to get the correct 16bits low for LCRNG
            res.append(second | low)

        k += ceil((LCRNGR_MUL_2 - r) / LCRNGR_SKIP1_2)

    return res

def lcrng_recover_lower_16bits_ivs_2(hp, atk, dfs, spa, spd, spe):
    first = (spe | (spa << 5) | (spd << 10)) << 16
    second = (hp | (atk << 5) | (dfs << 10)) << 16
    
    k = 0
    t = (second - LCRNGR_MUL_2 * first - LCRNGR_SUB_2) & 0x7fffffff
    x = (t * LCRNGR_PRIME_2) % LCRNGR_MUL_2
    kmax = (LCRNGR_BASE_2 - t) >> 31
    
    res = []
    while k <= kmax: # at most 188 iterations
        r = (x + LCRNGR_SKIP2_2 * k) % LCRNGR_MUL_2
        if r % LCRNGR_PRIME_2 == 0 and r < LCRNGR_RMAX_2:
            tmp = t + k * 0x80000000
            low = ((tmp // LCRNGR_MUL_2) * 0x95D9 + 0xB126) & 0xffff # backward of 2 states to get the correct 16bits low for LCRNG
            s = second | low
            res.extend((s, s ^ 0x80000000))

        k += ceil((LCRNGR_MUL_2 - r) / LCRNGR_SKIP2_2)

    return res

def channel_recover_lower_27bits_ivs(hp, atk, dfs, spa, spd, spe):
    first = hp << 27

    k = 0
    t = ((spe << 27) - GCRNG_MUL_3 * first - GCRNG_SUB_3) & 0xffffffff
    x = (t * GCRNG_PRIME_3) % GCRNG_MUL_3
    kmax = (GCRNG_BASE_3 - t) >> 32

    res = []
    while k <= kmax: # at most 209 131 iterations
        r = (x + GCRNG_SKIP_3 * k) % GCRNG_MUL_3
        if m := -r % GCRNG_PRIME_3: 
            r += m * GCRNG_SKIP_3 # to make r divisible by 3 (GCRNG_SKIP_3 % 3 == 1)
            k += m
        tmp = t + 0x100000000 * k
   
        while r < GCRNG_RMAX_3 and k <= kmax: # 21 iterations in average
            s = first | (tmp // GCRNG_MUL_3)

            test = (s * 0x343FD + 0x269EC3) & 0xffffffff
            if (test >> 27) == atk:
                test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                if (test >> 27) == dfs:
                    test = (test * 0xA9FC6809 + 0x1E278E7A) & 0xffffffff # jump on the speed iv since we know he matches
                    if (test >> 27) == spa:
                        test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                        if (test >> 27) == spd:
                            res.append(s)

            r += GCRNG_PRIME_3 * GCRNG_SKIP_3 # to keep r divisible by 3 
            k += GCRNG_PRIME_3
            tmp += GCRNG_ADD_3
             
        k += ceil((GCRNG_MUL_3 - r) / GCRNG_SKIP_3)

    return res

def channel_test(hp, atk, dfs, spa, spd, spe):
    hp  <<= 11
    atk <<= 11
    res = []
    for bits in range(1 << 22):
        pid = ((hp | (bits >> 11)) << 16) | atk | (bits & 0x7ff)
        for seed in gcrng_recover_lower_16bits_pid(pid):
            test = (seed * 0xA9FC6809 + 0x1E278E7A) & 0xffffffff # advance of 2 states to check def iv
            if (test >> 27) == dfs:
                test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                if (test >> 27) == spe:
                    test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                    if (test >> 27) == spa:
                        test = (test * 0x343FD + 0x269EC3) & 0xffffffff
                        if (test >> 27) == spd:
                            res.append(seed)
    return res