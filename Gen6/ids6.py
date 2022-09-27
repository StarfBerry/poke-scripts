### Script to search for tid (and tsv) with calibration from any date for Gen 6 games using Citra ###

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from datetime import datetime, timedelta
from RNG import TinyMT

def search_id(dt_start, dt_end, state, search_for_tid_tsv, tid, tsv, min_advc, max_advc):
    seed = TinyMT.recover_seed_from_state(state)

    if seed == -1:
        print("The TinyMT initial seed has not been recovered.")
        return 

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
                sid_ = rnd >> 16
                tsv_ = (tid_ ^ sid_) >> 4
                dt_ = dt_start + timedelta(seconds=second)
                s_ = TinyMT.backward_state(rng.state, advc+1) # TinyMT state we should obtain on the language selection screen 
                print(fmt.format(dt_, advc, tid_, sid_, tsv_, *s_))
        
        seed += 1000
    
    print("Research complete.")

if __name__ == "__main__":
    dt_start = datetime(2013, 10, 12, 0, 0, 0) # datetime of the calibration
    state = [0xc160ca69, 0xf8b93bad, 0x30303e61, 0x5499792d] # TinyMT state from the language selection screen obtained with dt_start
    dt_end = datetime(2014, 1, 1, 0, 0, 0) # datetime to stop the research (don't forget it's python)

    search_for_tid_tsv = True 
    tid = 5
    tsv = 42

    min_advc = 30
    max_advc = 80

    search_id(dt_start, dt_end, state, search_for_tid_tsv, tid, tsv, min_advc, max_advc)