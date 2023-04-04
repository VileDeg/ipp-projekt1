import sys

code = 0
g = sys.modules[__name__]

def xmlformat(txt: str = ""):
    g.code = 31
    raise Exception("XML format: " + txt)

def xmlstruct(txt: str = ""):
    g.code = 32
    raise Exception("XML structure: " + txt)

def sembase(txt: str = ""):
    g.code = 52
    raise Exception("Semantic (label/variable): " + txt)

def argtype(txt: str = ""):
    g.code = 53
    raise Exception("Invalid argument type: " + txt)

def novar(txt: str = ""):
    g.code = 54
    raise Exception("Variable not declared: " + txt)

def frame(txt: str = ""):
    g.code = 55
    raise Exception("Invalid or empty frame: " + txt)

def noval(txt: str = ""):
    g.code = 56
    raise Exception("Missing value: " + txt)

def badval(txt: str = ""):
    g.code = 57
    raise Exception("Division by zero: " + txt)

def badstr(txt: str = ""):
    g.code = 58
    raise Exception("String: " + txt)

def intern(txt: str = ""):
    g.code = 99
    raise Exception("Internal: " + txt)