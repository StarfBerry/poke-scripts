def ask(question):
    return input(question) in "Yy"

def ask_int(question, base=10, condition=None):
    val = int(input(question), base)
    if condition:
        while not condition(val):
            val = int(input(question), base)
    return val

def ask_float(question, condition=None):
    val = float(input(question))
    if condition:
        while not condition(val):
            val = float(input(question))
    return val