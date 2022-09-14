import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from Util import ask_int, valid_year, valid_month, valid_second, seed_to_time_4

seed = ask_int("Seed: 0x", 16) & 0xffffffff
year = ask_int("Year: ", condition=valid_year)
month = ask_int("Month: ", condition=valid_month)
second = ask_int("Second: ", condition=valid_second)

print()

res, delay = seed_to_time_4(seed, year, month, second)

if len(res) == 0:
    print("No results :(")
else:
    print(f"Delay: {delay}")
    for dt in res:
        print(dt)