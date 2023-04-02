import sys

DEBUG = False

def log(s):
    if DEBUG:
        print(s)

def err_call(func):
    def wrapper(*args, **kwargs):
        log(f'Error {func.__name__}')
        return func(*args, **kwargs)
    return wrapper

code = 0
g = sys.modules[__name__]

@err_call
def xmlformat(txt: str = ""):
    g.code = 31
    raise Exception("XML format: " + txt)
@err_call
def xmlstruct(txt: str = ""):
    g.code = 32
    raise Exception("XML structure: " + txt)
@err_call
def sembase(txt: str = ""):
    g.code = 52
    raise Exception("Semantic (label/variable): " + txt)
@err_call
def argtype(txt: str = ""):
    g.code = 53
    raise Exception("Invalid argument type: " + txt)
@err_call
def novar(txt: str = ""):
    g.code = 54
    raise Exception("Variable not declared: " + txt)
@err_call
def frame(txt: str = ""):
    g.code = 55
    raise Exception("Invalid or empty frame: " + txt)
@err_call
def noval(txt: str = ""):
    g.code = 56
    raise Exception("TODO: " + txt) #TODO: description
@err_call
def badval(txt: str = ""):
    g.code = 57
    raise Exception("Division by zero: " + txt)
@err_call
def badstr(txt: str = ""):
    g.code = 58
    raise Exception("String: " + txt) #TODO: description
@err_call
def intern(txt: str = ""):
    g.code = 99
    raise Exception("Internal: " + txt)