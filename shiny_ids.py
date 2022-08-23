import sys
sys.path.append(".")
sys.path.append("../")

from Util import ask_int, u32, u16

pid = u32(ask_int("PID: 0x", 16))
tid = u16(ask_int("TID: "))
gen = u16(ask_int("What Gen ? "))

x = 8 if gen < 6 else 16
pxor = (pid >> 16) ^ (pid & 0xffff) ^ tid

print(f"\n|  SID  |  XOR  |")
print("-----------------")

for xor in range(x):
    sid = pxor ^ xor
    print(f"| {sid:05d} | {xor:^5} |")

print("-----------------")