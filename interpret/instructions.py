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
    if g.temp_frame is None:
        raise InvalidOrEmptyFrameError()
    g.frame_stack.append(g.temp_frame)
    g.temp_frame = None

def ipopframe(_: Instruction):
    if len(g.frame_stack) == 0:
        raise InvalidOrEmptyFrameError()
    g.temp_frame = g.frame_stack.pop()

def idefvar(i: Instruction):
    if i.arg1.type != "var":
        raise ArgumentTypeError()
    if i.arg1.val in get_frame(i.arg1):
        raise SemanticCommonError("Variable is already defined.")

    get_frame(i.arg1)[i.arg1.val] = Expression(None, None)

def icall(i: Instruction): 
    ijump(i)
    g.return_stack.append(g.instructions.index(i))

def ireturn(_: Instruction):
    if len(g.return_stack) == 0:
        raise MissingValueError()
    g.inst_index = g.return_stack.pop()

def ipushs(i: Instruction):
    g.data_stack.append(symb(i.arg1))

def ipops(i: Instruction):
    if i.arg1.type != "var":
        raise ArgumentTypeError()
    if len(g.data_stack) == 0:
        raise MissingValueError()
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
        raise ArgumentTypeError()
    
    get_var(i.arg1).type = "bool"
    get_var(i.arg1).val = not v1.val

def iint2char(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "int":
        raise ArgumentTypeError()

    var = i.arg1
    get_var(var).type = "string"
    try:
        get_var(var).val = chr(int(v1.val))
    except ValueError as e:
        raise StringError() from e

def istri2int(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        raise ArgumentTypeError()

    var = i.arg1
    get_var(var).type = "int"
    if v2.val < 0 or v2.val >= len(v1.val):
        raise StringError()
    try:
        get_var(var).val = ord(v1.val[v2.val]) # int(v2.val)
    except IndexError as e:
        raise StringError() from e

def iread(i: Instruction):
    var = i.arg1

    inp = g.input_file.readline()
    if inp == "":
        get_var(var).type = "nil"
        get_var(var).val  = "nil"
        return
    inpstr = inp.strip()
    get_var(var).val  = inpstr

    atype = i.arg2.val
    get_var(var).type = atype

    if atype == "int":
        try:
            get_var(var).val = int(inpstr)
        except ValueError: # Error
            get_var(var).type = "nil"
    elif atype == "bool":
        get_var(var).val = inpstr.lower() == "true"
    elif atype == "string":
        try:
            get_var(var).val = parse_string(inpstr)
        except Exception: # Error
            get_var(var).type = "nil"
    elif atype == "float":
        try:
            get_var(var).val = float.fromhex(inpstr)
        except Exception: # Error
            try:
                get_var(var).val = float(inpstr)
            except ValueError:
                get_var(var).type = "nil"
    else:
        raise ArgumentTypeError()

def iwrite(i: Instruction, outstream=sys.stdout):
    v1 = symb(i.arg1)
    out = ""
    if v1.type in ["int", "string"]:
        out = v1.val
    elif v1.type == "float":
        out = str(float.hex(v1.val))
    elif v1.type == "bool":
        out = str(v1.val).lower()
    elif v1.type != "nil":
        raise ArgumentTypeError()
    print(out, file=outstream, end="")

def iconcat(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "string":
        raise ArgumentTypeError()
    
    var = i.arg1
    get_var(var).type = "string"
    get_var(var).val = v1.val + v2.val

def istrlen(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "string":
        raise ArgumentTypeError()
    
    var = i.arg1
    get_var(var).type = "int"
    get_var(var).val = len(v1.val)

def igetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        raise ArgumentTypeError()
    
    var = i.arg1
    get_var(var).type = "string"
    if v2.val < 0 or v2.val >= len(v1.val):
        raise StringError("Index out of range.")
    get_var(var).val = v1.val[v2.val]

def isetchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    var = i.arg1
    if get_var(var).val is None:
        raise MissingValueError()
    if get_var(var).type != "string":
        raise ArgumentTypeError()
    if v1.type != "int" or v2.type != "string":
        raise ArgumentTypeError()

    if v2.val == "":
        raise StringError("Empty string.")
    if v1.val < 0 or v1.val >= len(get_var(var).val):
        raise StringError("Index out of range.")

    tmplist = list(get_var(var).val)
    tmplist[v1.val] = v2.val[0]
    get_var(var).val = "".join(tmplist)

def itype(i: Instruction):
    var = i.arg1

    v1 = symb(i.arg2, True)

    typestr = v1.type
    if typestr is None:
        typestr = ""

    get_var(var).type  = "string"
    get_var(var).val = typestr

def ilabel(i: Instruction):
    if i.arg1.type != "label":
        raise ArgumentTypeError()
    lb = i.arg1.val
    if lb in g.labels:
        raise SemanticCommonError("Label already defined")
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
        raise ArgumentTypeError()

    if v1.val < 0 or v1.val > 49:
        raise InvalidValueError("Invalid error code")
    
    g.exit_code = v1.val
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
        raise ArgumentTypeError()
    get_var(i.arg1).type = "float"
    get_var(i.arg1).val = float(v1.val)

def ifloat2int(i: Instruction):
    v1 = symb(i.arg2)
    if v1.type != "float":
        raise ArgumentTypeError()
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
