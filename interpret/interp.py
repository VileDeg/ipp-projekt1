import io
import re
import sys
import xml.etree.ElementTree as et

from interp_classes import *

import error

DEBUG = False

def log(s):
    if DEBUG:
        print(s)

source_file  = None
instructions = []

frame_stack = []
glob_frame  = {}
temp_frame  = {}

labels     = {} # {label_name: instruction}
inst_index = 0

g = sys.modules[__name__]
    
def validate_xml(xml_tree: et.ElementTree):
    prog = xml_tree.getroot()
    log(f"{prog.tag=}")
    if prog.tag != "program":
        error.xmlstruct()
    ra = list(prog.attrib.keys())
    log(f"{ra=}")
    if not('language' in ra) and prog.attrib['language'] != "IPPcode23": # TODO: description, name
        error.xmlstruct()
    
    for inst in prog:
        log(f"\t{inst.tag=}")
        if inst.tag != "instruction":
            error.xmlstruct()
        ca = list(inst.attrib.keys())
        log(f"\t{ca=}")
        if not('order' in ca) or not('opcode' in ca):
            error.xmlstruct()
        
        for arg in inst:
            log(f"\t\t{arg.tag=}")
            if not(re.match(r"arg[123]", arg.tag)):
                error.xmlstruct()
            sa = list(arg.attrib.keys())
            log(f"\t\t{sa=}")
            if not('type' in sa):
                error.xmlstruct()
            
            log(f"\t\t{arg.text=}")
    return prog

def fill_instructions(prog: et.ElementTree):
    for inst in prog:
        order  = int(inst.attrib['order'])
        opcode = inst.attrib['opcode']

        inst_obj = Instruction(order, opcode)

        for arg in inst:
            arg_type = arg.attrib['type']
            value = arg.text
            try:
                inst_obj.add_operand(arg_type, value)
            except Exception as e:
                error.xmlstruct(str(e))

        instructions.append(inst_obj)
            
    # sort intructions by order
    instructions.sort(key=lambda x: x.order)

def initialize(source_file: io.TextIOWrapper):
    g.source_file  = source_file

    xml_tree = et.parse(g.source_file)

    prog = validate_xml(xml_tree)

    fill_instructions(prog)

def get_frame(var: str):
    pref = var[0:2]
    if pref == "TF":
        return temp_frame
    elif pref == "LF":
        if len(frame_stack) == 0:
            error.frame()
        return frame_stack[-1]
    elif pref == "GF":
        return glob_frame
    else:
        error.frame()
    
def get_var(var: str):
    return get_frame(var)[var[3:]]

def is_var_declared(var: str):
    return var[3:] in get_frame(var)

def is_var_defined(var: str):
    return is_var_declared(var) and get_var(var).value != None

# Instruction functions
def i_move(i: Instruction):
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


def i_createframe(_: Instruction):
    g.temp_frame = {}

def i_pushframe(_: Instruction):
    frame_stack.append(temp_frame)
    g.temp_frame = {}

def i_popframe(_: Instruction):
    g.temp_frame = frame_stack.pop()

def i_defvar(i: Instruction):
    if i.arg1.type != "var":
        error.argtype()
    var = i.arg1.text
    get_frame(var)[var[3:]] = Expression(None, None)

def get_var_if_def(var: str):
    if not is_var_defined(var):
        error.novar()
    return get_var(var)

def symb(op: Operand):
    if op.type == "var":
        return get_var_if_def(op.text)
    else:
        return Expression(op.type, op.text)

def var_symb(i: Instruction):
    if not is_var_declared(i.arg1.text):
        error.novar()
    
    v1 = symb(i.arg2)

    return v1

def var_symb_symb(i: Instruction):
    v1 = var_symb(i)
    v2 = symb(i.arg3)

    return v1, v2

def arithm(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)
    
    if v1.type != "int" or v2.type != "int":
        error.argtype()

    var = i.arg1.text
    get_var(var).type = "int"
    if   op == "add":
        get_var(var).value = int(v1.value) + int(v2.value)
    elif op == "sub":
        get_var(var).value = int(v1.value) - int(v2.value)
    elif op == "mul":
        get_var(var).value = int(v1.value) * int(v2.value)
    elif op == "idiv":
        get_var(var).value = int(v1.value) // int(v2.value)
    else:
        error.intern()

def i_add(i: Instruction):
    arithm(i, "add")

def i_sub(i: Instruction):
    arithm(i, "sub")

def i_mul(i: Instruction):
    arithm(i, "mul")

def i_idiv(i: Instruction):
    arithm(i, "idiv")

def relational(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    if v1.type != v2.type:
        error.argtype()
    if v1.type != "int" and v1.type != "string" and v1.type != "bool":
        error.argtype()
    
    var = i.arg1.text
    if   op == "lt":
        get_var(var).value = v1.value < v2.value
    elif op == "gt":
        get_var(var).value = v1.value > v2.value
    elif op == "eq":
        get_var(var).value = v1.value == v2.value
    else:
        error.intern()

def i_lt(i: Instruction):
    relational(i, "lt")

def i_gt(i: Instruction):
    relational(i, "gt")

def i_eq(i: Instruction):
    relational(i, "eq")

def and_or(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    if v1.type != "bool" or v2.type != "bool":
        error.argtype()
    
    var = i.arg1.text
    if   op == "and":
        get_var(var).value = v1.value and v2.value
    elif op == "or":
        get_var(var).value = v1.value or  v2.value
    else:
        error.intern()

def i_and(i: Instruction):
    and_or(i, "and")

def i_or(i: Instruction):
    and_or(i, "or")

def i_not(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "bool":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).value = not v1.value

def i_int2char(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "int":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "string"
    try:
        get_var(var).value = chr(int(v1.value))
    except ValueError:
        error.badstr()

def i_stri2int(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "int"
    try:
        get_var(var).value = ord(v1.value[int(v2.value)])
    except IndexError:
        error.badstr()

def i_read(i: Instruction):
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

def i_write(i: Instruction, outstream=sys.stdout):
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

def i_concat(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "string":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "string"
    get_var(var).value = v1.value + v2.value

def i_strlen(i: Instruction):
    v1 = var_symb(i)

    if v1.type != "string":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "int"
    get_var(var).value = len(v1.value)

def i_getchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "string" or v2.type != "int":
        error.argtype()
    
    var = i.arg1.text
    get_var(var).type = "string"
    try:
        get_var(var).value = v1.value[int(v2.value)]
    except IndexError:
        error.badstr()

def i_setchar(i: Instruction):
    v1, v2 = var_symb_symb(i)

    if v1.type != "int" or v2.type != "string":
        error.argtype()
    
    var = i.arg1.text
    try:
        get_var(var).value[v1.value] = v2.value[0]
    except IndexError:
        error.badstr()

def i_type(i: Instruction):
    v1 = symb(i.arg2)
    typestr = v1.type

    var = i.arg1.text
    if not is_var_defined(var):
        typestr = ""

    get_var(var).type  = "string"
    get_var(var).value = typestr

def i_label(i: Instruction):
    lb = i.arg1.text
    if lb in labels:
        error.sembase()
    labels[lb] = instructions.index(i) + 1

def i_jump(i: Instruction):
    lb = i.arg1.text
    if not lb in labels:
        error.sembase()
    g.inst_index = labels[lb]

def i_jumpifeq(i: Instruction):
    v1, v2 = symb(i.arg2), symb(i.arg3)
    if v1.type != v2.type: # TODO: nil
        g.exit_code = 53
        error.argtype()
    if v1.value == v2.value:
        i_jump(i)

def i_jumpifneq(i: Instruction):
    v1, v2 = symb(i.arg2), symb(i.arg3)
    if v1.type != v2.type: # TODO: nil
        g.exit_code = 53
        error.argtype()
    if v1.value != v2.value:
        i_jump(i)

def i_exit(i: Instruction):
    v1 = symb(i.arg1)
    if v1.type != "int":
        g.exit_code = 53
        error.argtype()

    if v1.value < 0 or v1.value > 49:
        error.badval()
    
    g.exit_code = v1.value
    g.inst_index = len(instructions)
    
def i_dprint(i: Instruction):
    i_write(i, sys.stderr)

def i_break():
    # Print out the current state of the program
    print("=== BREAK ===")
    print("Global frame:")
    for name, var in glob_frame.items():
        print(f"\t{name}: {var.type} {var.value}")
    print("Local frame:")
    for name, var in frame_stack[-1].items():
        print(f"\t{name}: {var.type} {var.value}")
    print("Temporary frame:")
    for name, var in temp_frame.items():
        print(f"\t{name}: {var.type} {var.value}")
    print("=== END OF BREAK ===")

def run():
    while g.inst_index < len(instructions):
        inst = instructions[g.inst_index]
        try:
            globals()[f"i_{inst.opcode.lower()}"](inst)
        except Exception:
            raise
        g.inst_index += 1
