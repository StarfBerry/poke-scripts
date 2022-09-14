### Script to search for tid (and tsv) with calibration from any date for Gen 6 games using Citra ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from datetime import datetime, timedelta
from RNG import TinyMT

### Settings ###

year = 2013
month = 10
day = 12
hour = 0
minute = 0
second = 0

st = [0xc160ca69, 0xf8b93bad, 0x30303e61, 0x5499792d] # TinyMT state from the language selection screen obtained with the datetime settings

tid = 5
tsv = 42
search_for_tid_tsv = True 

min_advc = 30
max_advc = 80
max_year = 2014 # Year to stop to the bruteforce

################

dt_start = datetime(year, month, day, hour, minute, second)

dt_end = datetime(max_year, 1, 1, 0, 0, 0)

seed = TinyMT.recover_seed_from_state(st)

if seed == -1:
    print("The TinyMT initial seed has not been recovered.")
    exit()

print(f"TinyMT Seed Calibration: {seed:08X}")
print("Searching...")
    
delta = dt_end - dt_start
seconds = int(delta.total_seconds())

if search_for_tid_tsv:
    check = lambda rnd: (tid_ := (rnd & 0xffff)) == tid and ((tid_ ^ (rnd >> 16)) >> 4) == tsv
else:
    check = lambda rnd: (rnd & 0xffff) == tid

fmt = "Date/Time: {} | Advances: {} | TID: {:05d} | SID: {:05d} | TSV: {:04d} | S[0]: {:08X} | S[1]: {:08X} | S[2]: {:08X} | S[3]: {:08X}"

# bruteforce
for second in range(seconds):
    rng = TinyMT(seed)
    rng.advance(2+min_advc)
    
    for advc in range(min_advc, max_advc):
        rnd = rng.next()
        if check(rnd):
            tid_ = rnd & 0xffff
            sid = rnd >> 16
            tsv_ = (tid_ ^ sid) >> 4
            dt = dt_start + timedelta(seconds=second)
            s = TinyMT.backward_state(rng.state, advc+1) # TinyMT state we should obtain on the language selection screen 
            print(fmt.format(dt, advc, tid_, sid, tsv_, *s))
    
    seed += 1000