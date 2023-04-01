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
def xmlformat():
    g.code = 31
    raise Exception("XML format")
@err_call
def xmlstruct(txt: str = ""):
    g.code = 32
    raise Exception("XML structure: " + txt)
@err_call
def sembase(txt: str = ""):
    g.code = 52
    raise Exception("Semantic (label/variable): " + txt)
@err_call
def argtype():
    g.code = 53
    raise Exception("Invalid argument type")
@err_call
def novar():
    g.code = 54
    raise Exception("Variable not declared")
@err_call
def frame():
    g.code = 55
    raise Exception("Invalid or empty frame")
@err_call
def noval():
    g.code = 56
    raise Exception("TODO:") #TODO: description
@err_call
def badval():
    g.code = 57
    raise Exception("Division by zero")
@err_call
def badstr():
    g.code = 58
    raise Exception("String:") #TODO: description
@err_call
def intern():
    g.code = 99
    raise Exception("Internal")