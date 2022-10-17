NATURES = (
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky")

TYPES = (
    "Fighting", "Flying", "Poison", "Ground",
    "Rock", "Bug", "Ghost", "Steel",
    "Fire", "Water", "Grass", "Electric",
    "Psychic", "Ice", "Dragon", "Dark")

def get_hp_type(ivs):
    s = (ivs[0] & 1) + 2 * (ivs[1] & 1) + 4 * (ivs[2] & 1) + 8 * (ivs[5] & 1) + 16 * (ivs[3] & 1) + 32 * (ivs[4] & 1)
    s *= 5/21
    return TYPES[int(s)]

def get_hp_damage(ivs):
    s = .5 * (ivs[0] & 2) + (ivs[1] & 2) + 2 * (ivs[2] & 2) + 4 * (ivs[5] & 2) + 8 * (ivs[3] & 2) + 16 * (ivs[4] & 2)
    s *= 40/63
    return int(s) + 30

def get_ivs(iv1, iv2):
    return [iv1 & 31, (iv1 >> 5) & 31, (iv1 >> 10) & 31, (iv2 >> 5) & 31, (iv2 >> 10) & 31, iv2 & 31]

def get_nature(rnd):
    return NATURES[rnd % 25]

def get_gender(rnd, female_ratio=1/2):
    return "Female" if rnd < int(255 * female_ratio) else "Male"

def get_psv(pid, rshift=3):
    return ((pid >> 16) ^ (pid & 0xffff)) >> rshift

def format_ivs(ivs):
    return ".".join(f"{iv:02d}" for iv in ivs)

def compare_ivs(min_ivs, max_ivs, ivs):
    return all(min_ivs[i] <= ivs[i] <= max_ivs[i] for i in range(6))

def compare_egg_ivs(egg_ivs, target_ivs):    
    for i, iv in enumerate(egg_ivs):
        if iv >= 0 and iv != target_ivs[i]:
            return False
    return True

class Pokemon:
    def __init__(self, gen=3, pid=None, pidh=None, pidl=None, nature=None, ivs=None, iv1=None, iv2=None, ability=None, gender=None, ec=None, seed=None):
        self.gen = gen
        self.pid = (pidh << 16) | pidl if pid is None else pid
        self.ec = self.pid if gen <= 5 else ec

        self.nature = get_nature(self.pid if gen <= 4 else nature) if nature != -1 else "Sync" 
        self.ivs = get_ivs(iv1, iv2) if ivs is None else ivs
        
        self.ability = ability if ability is not None else self.pid & 1 if gen <= 4 else (self.pid >> 16) & 1
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
        out += f"Gender: {self.gender:3d} | " if type(self.gender) == int else f"Gender: {self.gender} | "
        out += f"Hidden Power: {self.hp_type} "
        if self.gen <= 5:
            out += str(self.hp_dmge)
        return out