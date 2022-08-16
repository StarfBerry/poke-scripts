### Script to search for tid (and tsv) with calibration from any date for Gen 6 games ###

from datetime import datetime, timedelta
from RNG import TinyMT

tid = 5
tsv = 42

search_for_tid_tsv = True

min_advc = 30
max_advc = 80

dt = datetime(2013, 10, 12, 0, 0, 0) # Citra RTC, the datetime to start the research
st = [0xc160ca69, 0xf8b93bad, 0x30303e61, 0x5499792d] # TinyMT state from the language selection screen obtained with the previous datetime

dt_max = datetime(2014, 1, 1, 0, 0, 0) # Max datetime for the bruteforce (don't forget it's python)

seed = TinyMT.recover_seed_from_state(st)

if seed == -1:
    print("The TinyMT initial seed has not been recovered.")
    exit()

print(f"TinyMT Seed Calibration: {seed:08X}")
print("Searching...")
    
delta = dt_max - dt
seconds = int(delta.total_seconds())

if search_for_tid_tsv:
    check = lambda rnd: (_tid := (rnd & 0xffff)) == tid and ((_tid ^ (rnd >> 16)) >> 4) == tsv
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
            _tid = rnd & 0xffff
            _sid = rnd >> 16
            _tsv = (_tid ^ _sid) >> 4
            _dt = dt + timedelta(seconds=second)
            _s = TinyMT.backward(rng.state, advc+1) # TinyMT state we should obtain on the language selection screen 
            print(fmt.format(_dt, advc, _tid, _sid, _tsv, *_s))
    
    seed += 1000