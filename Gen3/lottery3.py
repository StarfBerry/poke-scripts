'''
Script to manipulate the lottery rng in RSE to get the Master Ball.
The lottery ticket is generated when you press A to load your save file.
'''

import sys
sys.path.append(".")
sys.path.append("../")

from RNG import LCRNG, MRNG

def generate_tickets(game, seed, max_advc, tids, days_since):
    print("| {:^10} | {} |".format("Advances", "Ticket"))
    print("-" * 23)
    fmt = "| {:<10} | {:05d}  |"

    rng = LCRNG(seed)
    rng.advance(25 if game == 0 else 83) # delay

    for advc in range(max_advc):
        ticket = MRNG(rng.rand()).advance(days_since) & 0xffff
        if ticket in tids:
            print(fmt.format(advc, ticket))
    
    print("-" * 23)

if __name__ == "__main__":
    from Util import ask_int, u32
    
    game = ask_int("Game (0=RS 1=Emerald) ? ")
    seed = ask_int("Initial Seed: 0x", 16) if game == 0 else 0 # Not possible to use the battle video/painting for this rng.
    max_advc = u32(ask_int("Max Advances: "))
    tids = [int(tid) for tid in input("Target TIDs (x.x.x...): ").split(".")]
    days_since = ask_int("How many days have elapsed since your previous save (can be 0): ") 
    print()
    generate_tickets(game, seed, max_advc, tids, days_since)