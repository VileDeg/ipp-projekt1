from interp_classes import *
from base import *
#from base import get_frame

# Instruction functions
def imove(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
    
    if not is_var_declared(i.arg1.text):
        error.novar()
    
    if i.arg2.type == "var":
        if not is_var_defined(i.arg2.text):
            error.novar()
        get_var(i.arg1.text).value = get_var(i.arg2.text).value
    else:
        get_var(i.arg1.text).type  = i.arg2.type
        get_var(i.arg1.text).value = i.arg2.text


def icreateframe(_: Instruction):
    g.temp_frame = {}

def ipushframe(_: Instruction):
    if g.temp_frame == None:
        error.frame()
    g.frame_stack.append(g.temp_frame)
    g.temp_frame = None

def ipopframe(_: Instruction):
    if len(g.frame_stack) == 0:
        error.frame()
    g.temp_frame = g.frame_stack.pop()

def idefvar(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
    var = i.arg1.text
    get_frame(var)[var[3:]] = Expression(None, None)

# TODO:
""" def icall(i: Instruction): 
    if i.arg1.type != "label":
        error.argtype()
    if not i.arg1.text in labels:
        error.sembase()
    g.inst_index = labels[i.arg1.text].order - 1

def ireturn(_: Instruction):
    g.inst_index = return_stack.pop()

def ipushs(i: Instruction):
    if i.arg1.type == "var":
        if not is_var_defined(i.arg1.text):
            error.novar()
        data_stack.append(get_var(i.arg1.text))
    else:
        data_stack.append(Expression(i.arg1.type, i.arg1.text))

def ipops(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
    if not is_var_declared(i.arg1.text):
        error.novar()
    if len(data_stack) == 0:
        error.stack()
    get_var(i.arg1.text).type  = data_stack[-1].type
    get_var(i.arg1.text).value = data_stack[-1].value
    data_stack.pop() """



def iadd(i: Instruction):
    arithm(i, "add")

def isub(i: Instruction):
    arithm(i, "sub")

def imul(i: Instruction):
    arithm(i, "mul")

def iidiv(i: Instruction):
    arithm(i, "idiv")



def ilt(i: Instruction):
    relational(i, "lt")

def igt(i: Instruction):
    relational(i, "gt")

def ieq(i: Instruction):
    relational(i, "eq")



def iand(i: Instruction):
    and_or(i, "and")

def ior(i: Instruction):
    and_or(i, "or")

def inot(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "bool":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).value = not v1.value

def iint2char(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "int":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "string"
    try:
        get_var(var).value = chr(int(v1.value))
    except ValueError:
        error.badstr()

def istri2int(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "int"
    try:
        get_var(var).value = ord(v1.value[int(v2.value)])
    except IndexError:
        error.badstr()

def iread(i: Instruction): #TODO: invalid input
    var = i.arg1.text
    if not is_var_defined(var):
        error.novar()
    
    type = i.arg2.text
    inpstr = input()
    if inpstr == "":
        get_var(var).type = "nil"
        get_var(var).value = "nil"
        return
    
    get_var(var).type  = "string"
    get_var(var).value = inpstr
    try:
        if type == "int":
            get_var(var).value = int(inpstr)
        elif type == "bool":
            if inpstr == "true":
                get_var(var).value = True
            elif inpstr == "false":
                get_var(var).value = False
            else:
                get_var(var).type = "nil"
                get_var(var).value = "nil"
        elif type == "string":
            pass
        else:
            error.badval() # TODO: maybe argtype?
    except ValueError:
        get_var(var).type = "nil"
        get_var(var).value = "nil"
    except Exception:
        raise        

def iwrite(i: Instruction, outstream=sys.stdout):
    v1 = symb(i.arg1)
    out = ""
    if v1.type == "int" or v1.type == "string":
        out = v1.value
    elif v1.type == "bool":
        out = str(v1.value).lower()
    elif v1.type == "nil":
        pass
    else:
        error.argtype()
    print(out, file=outstream, end="")

def iconcat(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "string":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "string"
    get_var(var).value = v1.value + v2.value

def istrlen(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "string":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "int"
    get_var(var).value = len(v1.value)

def igetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "string"
    try:
        get_var(var).value = v1.value[int(v2.value)]
    except IndexError:
        error.badstr()

def isetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "int" or v2.type != "string":
        error.argtype()
    
    var = i.arg1.text
    try:
        get_var(var).value[v1.value] = v2.value[0]
    except IndexError:
        error.badstr()

def itype(i: Instruction):
    v1 = symb(i.arg2)
    typestr = v1.type

    var = i.arg1.text
    if not is_var_defined(var):
        typestr = ""

    get_var(var).type  = "string"
    get_var(var).value = typestr

def ilabel(i: Instruction):
    lb = i.arg1.text
    if lb in g.labels:
        error.sembase()
    g.labels[lb] = g.instructions.index(i)

def ijump(i: Instruction):
    lb = i.arg1.text
    if not lb in g.labels:
        error.sembase()
    g.inst_index = g.labels[lb]

def ijumpifeq(i: Instruction):
    v1, v2 = symb(i.arg2), symb(i.arg3)
    if v1.type != v2.type: # TODO: nil
        error.argtype()
    if v1.value == v2.value:
        ijump(i)

def ijumpifneq(i: Instruction):
    v1, v2 = symb(i.arg2), symb(i.arg3)
    if v1.type != v2.type: # TODO: nil
        error.argtype()
    if v1.value != v2.value:
        ijump(i)

def iexit(i: Instruction):
    v1 = symb(i.arg1)
    if v1.type != "int":
        error.argtype()

    if v1.value < 0 or v1.value > 49:
        error.badval()
    
    g.exit_code = v1.value
    g.inst_index = len(g.instructions)
    
def idprint(i: Instruction):
    iwrite(i, sys.stderr)

def ibreak():
    # Print out the current state of the program
    print("=== BREAK ===")
    print("Global frame:")
    for name, var in g.glob_frame.items():
        print(f"\t{name}: {var.type} {var.value}")
    print("Local frame:")
    for name, var in g.frame_stack[-1].items():
        print(f"\t{name}: {var.type} {var.value}")
    print("Temporary frame:")
    for name, var in g.temp_frame.items():
        print(f"\t{name}: {var.type} {var.value}")
    print("=== END OF BREAK ===")