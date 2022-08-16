natures = (
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky")

types = (
    "Fighting", "Flying", "Poison", "Ground",
    "Rock", "Bug", "Ghost", "Steel",
    "Fire", "Water", "Grass", "Electric",
    "Psychic", "Ice", "Dragon", "Dark")

order = (0, 1, 2, 5, 3, 4)

def get_hp_type(ivs):
    index = int(sum(2**p * (ivs[i] & 1) for p, i in enumerate(order)) * 5/21)
    return types[index]

def get_hp_damage(ivs):
    return int(sum(2**(p-1) * (ivs[i] & 2) for p, i in enumerate(order)) * 40/63) + 30

def get_ivs(iv1, iv2):
    ivs = (iv2 << 15) | (iv1 & 0x7fff)
    return [(ivs >> (order[i] * 5)) & 0x1f for i in order]

def get_gender(rnd, female_ratio=2):
    return "Female" if rnd < (256 // female_ratio) else "Male"

def get_nature(rnd):
    return natures[rnd % 25]

def get_psv(pid, rshift=3):
    return ((pid >> 16) ^ (pid & 0xffff)) >> rshift

def format_ivs(ivs):
    return ".".join(f"{iv:02d}" for iv in ivs)

def compare_ivs(min_ivs, max_ivs, target_ivs):
    return all(min_ivs[i] <= iv <= max_ivs[i] for i, iv in enumerate(target_ivs))

def compare_ivs_egg(egg_ivs, target_ivs):
    for i, iv in enumerate(egg_ivs):
        if type(iv) == int and iv != target_ivs[i]:
            return False
    return True

class Pokemon:
    def __init__(self, gen=3, gc=False, pid=None, pidh=None, pidl=None, nature=None, ivs=None, iv1=None, iv2=None, ability=None, gender=None, ec=None, seed=None):
        self.gen = gen
        self.pid = (pidh << 16) | pidl if pid is None else pid
        self.ec = self.pid if gen <= 5 else ec

        self.nature = get_nature(self.pid if gen <= 4 else nature) if nature != -1 else "Sync" 
        self.ivs = get_ivs(iv1, iv2) if ivs is None else ivs
        
        self.ability = self.pid & 1 if gen <= 4 and not gc else (self.pid >> 16) & 1 if gen == 5 else ability
        self.gender = self.pid & 0xff if gen <= 5 else gender
        self.seed = seed

        self.hp_type = get_hp_type(self.ivs)
        self.hp_dmge = get_hp_damage(self.ivs) if gen <= 5 else 60
        self.psv = get_psv(self.pid, 3 if gen <= 5 else 4)
    
    def __repr__(self):
        out = ""
        if self.seed is not None:
            out += f"Seed: {self.seed:08X} | "
        if self.gen >= 6:
            out += f"EC: {self.ec:08X} | "
        out += f"PID: {self.pid:08X} | "
        out += f"PSV: {self.psv:4d} | "
        out += f"Nature: {self.nature:7s} | "
        out += f"Ability: {self.ability} | " 
        out += f"IVs: {format_ivs(self.ivs)} | "
        out += f"Gender: {self.gender:5d} | " if type(self.gender) == int else f"Gender: {self.gender} | "
        out += f"Hidden Power: {self.hp_type} "
        if self.gen <= 5:
            out += str(self.hp_dmge)
        return out