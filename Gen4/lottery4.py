### Script to mess with the Gen 4 lottery rng ###

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import LCRNG, LCRNGR, MRNG, MRNGR, ARNG
from datetime import date, timedelta

DAYS = 36524 # Number of days between 2000-01-01 and 2099-12-31
MAX_DATE = date(2099, 12, 31)

def recover_lottery_seed_4(t1, t2, t3, hgss=True):
    lotto_advc, lotto_back = (LCRNG, LCRNGR) if hgss else (MRNG, MRNGR)
    high = t1 << 16
    for low in range(0x10000):
        seed = lotto_back(high | low).next()
        day = ARNG(seed)
        if lotto_advc(day.next()).rand() == t2 and lotto_advc(day.next()).rand() == t3:
            return seed
    return -1

def generate_winning_tickets(seed, ids, date_start, max_advc, hgss=True):
    lotto_advc = LCRNG if hgss else MRNG
    day = ARNG(seed)
    for advc in range(1, max_advc):
        ticket = lotto_advc(day.next()).rand()
        if ticket in ids:
            date = date_start + timedelta(days=advc)
            cycle = 0
            while date > MAX_DATE:
                cycle += 1
                date -= timedelta(days=DAYS)
            print(f"Advances: {advc:7d} | Ticket: {ticket:05d} | PRNG State: {day.state:08X} | Cycle: {cycle} | Date: {date}")

if __name__ == "__main__":
    date = date(2022, 6, 29) # date from t1
    hgss = False
    t1 = 57099
    t2 = 33596
    t3 = 25979
    seed = recover_lottery_seed_4(t1, t2, t3, hgss)
    target_ids = [5, 10101]
    max_advc = 100_000
    
    if seed == -1:
        print("The lottery prng state has not been recovered.")
        exit()
    else:
        print(f"Recovered Seed: {seed:08X}\n")
        generate_winning_tickets(seed, target_ids, date, max_advc, hgss)