import sys

from classes import *
from base import *

def imove(i: Instruction):
    v1 = symb(i.arg2)
    get_var(i.arg1).type = v1.type
    get_var(i.arg1).val = v1.val

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
    if i.arg1.val in get_frame(i.arg1):
        error.sembase("Variable is already defined.")

    get_frame(i.arg1)[i.arg1.val] = Expression(None, None)

def icall(i: Instruction): 
    ijump(i)
    g.return_stack.append(g.instructions.index(i))

def ireturn(_: Instruction):
    if len(g.return_stack) == 0:
        error.noval()
    g.inst_index = g.return_stack.pop()

def ipushs(i: Instruction):
    g.data_stack.append(symb(i.arg1))

def ipops(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
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

def idiv(i: Instruction):
    arithm(i, "div")

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
    
    get_var(i.arg1).type = "bool"
    get_var(i.arg1).val = not v1.val

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
    if v2.val < 0 or v2.val >= len(v1.val):
        error.badstr()
    try:
        get_var(var).val = ord(v1.val[v2.val]) # int(v2.val)
    except IndexError:
        error.badstr()

def iread(i: Instruction):
    var = i.arg1

    inp = g.input_file.readline()
    if inp == "":
        get_var(var).type = "nil"
        get_var(var).val  = "nil"
        return
    inpstr = inp.strip()
    get_var(var).val  = inpstr
    
    type = i.arg2.val
    get_var(var).type = type

    if   type == "int":
        try:
            get_var(var).val = int(inpstr)
        except ValueError: # Error
            get_var(var).type = "nil"
    elif type == "bool":
        if inpstr.lower() == "true":
            get_var(var).val = True
        else:
            get_var(var).val = False
        # else: # Error
        #     get_var(var).type = "nil"
    elif type == "string":
        try:
            get_var(var).val = parse_string(inpstr)
        except Exception: # Error
            get_var(var).type = "nil"
    elif type == "float":
        try:
            get_var(var).val = float.fromhex(inpstr)
        except Exception: # Error
            try:
                get_var(var).val = float(inpstr)
            except ValueError:
                get_var(var).type = "nil"
    else:
        error.badval() # TODO: maybe argtype?

def iwrite(i: Instruction, outstream=sys.stdout):
    v1 = symb(i.arg1)
    out = ""
    if   v1.type == "int" or v1.type == "string":
        out = v1.val
    elif v1.type == "float":
        out = str(float.hex(v1.val))
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
    if v2.val < 0 or v2.val >= len(v1.val):
        error.badstr("Index out of range.")
    get_var(var).val = v1.val[v2.val]

def isetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    var = i.arg1
    if get_var(var).val == None:
        error.noval()
    if get_var(var).type != "string":
        error.argtype()
    if v1.type != "int" or v2.type != "string":
        error.argtype()

    if v2.val == "":
        error.badstr("Empty string.")
    if v1.val < 0 or v1.val >= len(get_var(var).val):
        error.badstr("Index out of range.")

    tmplist = list(get_var(var).val)
    tmplist[v1.val] = v2.val[0]
    get_var(var).val = "".join(tmplist)

def itype(i: Instruction):
    var = i.arg1

    v1 = symb(i.arg2, True)

    typestr = v1.type
    if typestr == None:
        typestr = ""

    get_var(var).type  = "string"
    get_var(var).val = typestr

def ilabel(i: Instruction):
    if i.arg1.type != "label":
        error.argtype()
    lb = i.arg1.val
    if lb in g.labels:
        error.sembase("Label already defined")
    g.labels[lb] = g.instructions.index(i)

def ijump(i: Instruction):
    jump(i, "j")

def ijumpifeq(i: Instruction):
    jump(i, "je")

def ijumpifneq(i: Instruction):
    jump(i, "jne")

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

def iint2float(i: Instruction):
    v1 = symb(i.arg2)
    if v1.type != "int":
        error.argtype()
    get_var(i.arg1).type = "float"
    get_var(i.arg1).val = float(v1.val)

def ifloat2int(i: Instruction):
    v1 = symb(i.arg2)
    if v1.type != "float":
        error.argtype()
    get_var(i.arg1).type = "int"
    get_var(i.arg1).val = int(v1.val)

def iclears(_: Instruction):
    g.data_stack.clear()

def iadds(i: Instruction):
    stack_inst(iadd, i, 2)

def isubs(i: Instruction):
    stack_inst(isub, i, 2)

def imuls(i: Instruction):
    stack_inst(imul, i, 2)

def iidivs(i: Instruction):
    stack_inst(iidiv, i, 2)

def idivs(i: Instruction):
    stack_inst(idiv, i, 2)

def ilts(i: Instruction):
    stack_inst(ilt, i, 2)

def igts(i: Instruction):
    stack_inst(igt, i, 2)

def ieqs(i: Instruction):
    stack_inst(ieq, i, 2)

def iands(i: Instruction):
    stack_inst(iand, i, 2)

def iors(i: Instruction):
    stack_inst(ior, i, 2)

def inots(i: Instruction):
    stack_inst(inot, i, 1)

def iint2chars(i: Instruction):
    stack_inst(iint2char, i, 1)

def istri2ints(i: Instruction):
    stack_inst(istri2int, i, 2)

def ijumpifeqs(i: Instruction):
    i.arg3 = g.data_stack.pop()
    i.arg2 = g.data_stack.pop()
    ijumpifeq(i)

def ijumpifneqs(i: Instruction):
    i.arg3 = g.data_stack.pop()
    i.arg2 = g.data_stack.pop()
    ijumpifneq(i)

def iint2floats(i: Instruction):
    stack_inst(iint2float, i, 1)

def ifloat2ints(i: Instruction):
    stack_inst(ifloat2int, i, 1)
