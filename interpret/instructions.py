from classes import *
from base import *

def imove(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
    
    if not is_var_declared(i.arg1):
        error.novar()
    
    if i.arg2.type == "var":
        if not is_var_declared(i.arg1):
            error.novar()
        if not is_var_defined(i.arg2):
            error.noval()
        get_var(i.arg1).val = get_var(i.arg2).val
    else:
        get_var(i.arg1).type  = i.arg2.type
        get_var(i.arg1).val = i.arg2.val

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
    get_frame(i.arg1)[i.arg1.val] = Expression(None, None)

def icall(i: Instruction): 
    ijump(i)
    g.return_stack.append(g.instructions.index(i))

def ireturn(_: Instruction):
    g.inst_index = g.return_stack.pop()

def ipushs(i: Instruction):
    g.data_stack.append(symb(i.arg1))

def ipops(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
    if not is_var_declared(i.arg1):
        error.novar()
    if len(g.data_stack) == 0:
        error.noval()
    top = g.data_stack.pop()
    get_var(i.arg1).type = top.type
    get_var(i.arg1).val  = top.val

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
    
    var = i.arg1
    get_var(var).val = not v1.val

def iint2char(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "int":
        error.argtype()
    
    var = i.arg1
    get_var(var).type = "string"
    try:
        get_var(var).val = chr(int(v1.val))
    except ValueError:
        error.badstr()

def istri2int(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        error.argtype()
    
    var = i.arg1
    get_var(var).type = "int"
    try:
        get_var(var).val = ord(v1.val[int(v2.val)])
    except IndexError:
        error.badstr()

def iread(i: Instruction):
    var = i.arg1
    if not is_var_declared(var):
        error.novar()

    inpstr = g.input_file.readline().strip()
    if inpstr == "": # Error
        get_var(var).type = "nil"
        return
    
    type = i.arg2.val
    get_var(var).type = type
    get_var(var).val  = inpstr

    if   type == "int":
        try:
            get_var(var).val = int(inpstr)
        except ValueError: # Error
            get_var(var).type = "nil"
    elif type == "bool":
        if inpstr == "true":
            get_var(var).val = True
        elif inpstr == "false":
            get_var(var).val = False
        else: # Error
            get_var(var).type = "nil"
    elif type == "string":
        try:
            get_var(var).val = parse_string(inpstr)
        except Exception: # Error
            get_var(var).type = "nil"
    else:
        error.badval() # TODO: maybe argtype?

def iwrite(i: Instruction, outstream=sys.stdout):
    v1 = symb(i.arg1)
    out = ""
    if   v1.type == "int" or v1.type == "string":
        out = v1.val
    elif v1.type == "bool":
        out = str(v1.val).lower()
    elif v1.type == "nil":
        pass
    else:
        error.argtype()
    print(out, file=outstream, end="")

def iconcat(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "string":
        error.argtype()
    
    var = i.arg1
    get_var(var).type = "string"
    get_var(var).val = v1.val + v2.val

def istrlen(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "string":
        error.argtype()
    
    var = i.arg1
    get_var(var).type = "int"
    get_var(var).val = len(v1.val)

def igetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        error.argtype()
    
    var = i.arg1
    get_var(var).type = "string"
    try:
        get_var(var).val = v1.val[int(v2.val)]
    except IndexError:
        error.badstr()

def isetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "int" or v2.type != "string":
        error.argtype()
    
    var = i.arg1
    try:
        get_var(var).val[v1.val] = v2.val[0]
    except IndexError:
        error.badstr()

def itype(i: Instruction):
    v1 = symb(i.arg2)
    typestr = v1.type

    var = i.arg1
    if not is_var_defined(var):
        typestr = ""

    get_var(var).type  = "string"
    get_var(var).val = typestr

def ilabel(i: Instruction):
    if i.arg1.type != "label":
        error.argtype()
    lb = i.arg1.val
    #print(f"{g.labels=}")
    if lb in g.labels:
        error.sembase("Label already defined")
    g.labels[lb] = g.instructions.index(i)

def ijump(i: Instruction):
    lb = i.arg1.val
    if not lb in g.labels:
        error.sembase()
    g.inst_index = g.labels[lb]

def ijumpifeq(i: Instruction):
    v1, v2 = symb(i.arg2), symb(i.arg3)
    if v1.type != v2.type: # TODO: nil
        error.argtype()
    if v1.val == v2.val:
        ijump(i)

def ijumpifneq(i: Instruction):
    v1, v2 = symb(i.arg2), symb(i.arg3)
    if v1.type != v2.type: # TODO: nil
        error.argtype()
    if v1.val != v2.val:
        ijump(i)

def iexit(i: Instruction):
    v1 = symb(i.arg1)
    if v1.type != "int":
        error.argtype()

    if v1.val < 0 or v1.val > 49:
        error.badval("Invalid error code")
    
    error.code = v1.val
    g.inst_index = len(g.instructions)
    
def idprint(i: Instruction):
    iwrite(i, sys.stderr)

def ibreak():
    # Print out the current state of the program
    print("=== BREAK ===")
    print("Global frame:")
    for name, var in g.glob_frame.items():
        print(f"\t{name}: {var.type} {var.val}")
    print("Local frame:")
    for name, var in g.frame_stack[-1].items():
        print(f"\t{name}: {var.type} {var.val}")
    print("Temporary frame:")
    for name, var in g.temp_frame.items():
        print(f"\t{name}: {var.type} {var.val}")
    print("=== END OF BREAK ===")