import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from datetime import datetime
from Util import days_in_month

def seed_to_time_4(seed, year=2000, target_month=1, target_second=0):    
    base = seed >> 24
    hour = (seed >> 16) & 0xff
    delay = ((seed & 0xffff) - (year % 2000)) & 0xffffffff

    if hour > 23:
        delay += (hour - 23) * 0x10000
        hour = 23
    
    res = []
    for month in range(target_month, target_month+1):
        for day in range(1, days_in_month(year, month)+1):
            md = month * day
            for minute in range(60):
                if (md + minute + target_second) & 0xff == base:
                    dt = datetime(year, month, day, hour, minute, target_second)
                    res.append(dt)
    
    return (res, delay)

def search_seed_4(seed, year, month, second):
    res, delay = seed_to_time_4(seed, year, month, second)

    if len(res) == 0:
        print("No results :(")
    else:
        print(f"Delay: {delay}")
        for dt in res:
            print(dt)

if __name__ == "__main__":
    from Util import u32, ask_int, valid_year, valid_month, valid_second

    seed = u32(ask_int("Seed: 0x", 16))
    year = ask_int("Year: ", condition=valid_year)
    month = ask_int("Month: ", condition=valid_month)
    second = ask_int("Second: ", condition=valid_second)

    print()

    search_seed_4(seed, year, month, second)