'''
Script to manipulate the lottery rng in RSE to get the Master Ball.
The lottery ticket is generated when you press A to load your save file.
'''

import os, sys
sys.path.append(os.path.dirname(__file__) + "\..")

from RNG import LCRNG, MRNG

def generate_winning_tickets_3(game, seed, max_advc, tids, days_since):
    print("| {:^10} | {} |".format("Advances", "Ticket"))
    print("-" * 23)
    fmt = "| {:<10} | {:05d}  |"

    rng = LCRNG(seed)
    rng.jump(25 if game == 0 else 83) # delay

    for advc in range(max_advc):
        ticket = MRNG(rng.next_u16()).advance(days_since) & 0xffff
        if ticket in tids:
            print(fmt.format(advc, ticket))
    
    print("-" * 23)

if __name__ == "__main__":
    from Util import ask_int, ask_ints, u32
    
    game = ask_int("Game (0=RS 1=Emerald) ? ")
    seed = ask_int("Initial Seed: 0x", 16) if game == 0 else 0 # Not possible to use the battle video/painting seed for this rng.
    max_advc = u32(ask_int("Max Advances: "))
    tids = ask_ints("Target TIDs (x.x.x...): ")
    days_since = ask_int("How many days have elapsed since your previous save (can be 0): ") 
    
    print()
    
    generate_winning_tickets_3(game, seed, max_advc, tids, days_since)