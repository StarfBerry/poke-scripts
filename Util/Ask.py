def ask(msg):
    return input(msg) in "Yy"

def ask_int(msg, base=10, condition=None):
    x = int(input(msg), base)
    if condition:
        while not condition(x):
            x = int(input(msg), base)
    return x

def ask_ints(msg, sep=".", base=10, condition=None):
    xs = [int(x, base) for x in input(msg).split(sep)]
    if condition:
        while not condition(xs):
            xs = [int(x, base) for x in input(msg).split(sep)]
    return xs

def ask_float(msg, condition=None):
    x = float(input(msg))
    if condition:
        while not condition(x):
            x = float(input(msg))
    return x