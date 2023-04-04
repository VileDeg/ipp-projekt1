import io
import re
import xml.etree.ElementTree as et

from classes import *

from error import *
import globals as g

def parse_xml(xml_tree: et.ElementTree):
    prog = xml_tree.getroot()
    if prog.tag != "program":
        raise XMLStructureError()
    ra = list(prog.attrib.keys())
    if 'language' not in ra and prog.attrib['language'] != "IPPcode23":
        raise XMLStructureError()

    for inst in prog:
        if inst.tag != "instruction":
            raise XMLStructureError()
        ca = list(inst.attrib.keys())
        if 'order' not in ca or 'opcode' not in ca:
            raise XMLStructureError()
        try:
            order = int(inst.attrib['order'])
        except ValueError as e:
            raise XMLStructureError("Order is not an integer") from e
        if order < 1:
            raise XMLStructureError("Invalid instruction order")

        opcode = inst.attrib['opcode'].lower()
        if opcode not in g.opcodes:
            raise XMLStructureError("Invalid opcode")

        # create instruction object
        inst_obj = Instruction(order, opcode)

        arglist = []
        argc = 1
        for arg in inst:
            if argc > g.opcodes[opcode]:
                raise XMLStructureError("Too many arguments")
            if not re.match(r"arg[1-3]", arg.tag):
                raise XMLStructureError("Invalid argument tag")
            sa = list(arg.attrib.keys())
            if 'type' not in sa:
                raise XMLStructureError()

            arg_type = arg.attrib['type'] #.lower()
            if arg_type not in ["int", "float", "bool", "string", "nil", "label", "type", "var"]:
                raise XMLStructureError("Invalid argument type")
            # Empty string edge case
            if arg_type == "string" and arg.text is None:
                arg.text = ""

            arglist.append((arg_type, arg.text, int(arg.tag[3])))

            argc += 1
        if argc - 1 < g.opcodes[opcode]:
            raise XMLStructureError("Too few arguments")

        arglist.sort(key=lambda x: x[2])

        for argc, triple in enumerate(arglist, start=1):
            if triple[2] != argc:
                raise XMLStructureError("Invalid argument order")
            # add operand to instruction
            try:
                inst_obj.add_operand(triple[0], triple[1])
            except Exception as e:
                raise XMLStructureError(str(e)) from e
        # add instruction to list
        g.instructions.append(inst_obj)

    # check for duplicates in instruction orders
    orders = [i.order for i in g.instructions]
    if len(orders) != len(set(orders)):
        raise XMLStructureError("Duplicate instruction order")
    # sort intructions by order
    g.instructions.sort(key=lambda x: x.order)

def initialize(input_file: io.TextIOWrapper, source_file: io.TextIOWrapper):
    g.input_file  = input_file
    g.source_file = source_file

    try:
        xml_tree = et.parse(g.source_file)
    except et.ParseError as e:
        raise XMLStructureError("XML parse error") from e

    parse_xml(xml_tree)
    g.stack_var = Operand("var", "GF@.STACK_RET")
    g.glob_frame[g.stack_var.val] = Expression(None, None)

def get_frame(op: Operand):
    if op.frame == Frame.TEMPORARY:
        if g.temp_frame is None:
            raise InvalidOrEmptyFrameError()
        return g.temp_frame
    elif op.frame == Frame.LOCAL:
        if len(g.frame_stack) == 0:
            raise InvalidOrEmptyFrameError()
        return g.frame_stack[-1]
    elif op.frame == Frame.GLOBAL:
        return g.glob_frame
    else:
        raise InternalError()
    
def get_var(op: Operand):
    try:
        return get_frame(op)[op.val]
    except KeyError as e:
        raise VariableNotDeclaredError() from e 

def symb(op: Operand, declared_only=False):
    if op.type != "var":
        return Expression(op.type, op.val)
    if not declared_only and get_var(op).val is None:
        raise MissingValueError()

    return get_var(op)

def var_symb(i: Instruction):
    if i.arg1.type != "var":
        raise ArgumentTypeError()

    return symb(i.arg2)

def var_symb_symb(i: Instruction):
    v1 = var_symb(i)
    v2 = symb(i.arg3)

    return v1, v2

def arithm(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    if v1.type != v2.type:
        raise ArgumentTypeError()
    if v1.type not in ["int", "float"]:
        raise ArgumentTypeError()

    get_var(i.arg1).type = v1.type
    if   op == "add":
        get_var(i.arg1).val = v1.val + v2.val
    elif op == "sub":
        get_var(i.arg1).val = v1.val - v2.val
    elif op == "mul":
        get_var(i.arg1).val = v1.val * v2.val
    elif op == "idiv":
        if v1.type != "int":
            raise ArgumentTypeError()
        if v2.val == 0:
            raise InvalidValueError()
        get_var(i.arg1).val = v1.val // v2.val
    elif op == "div":
        if v1.type != "float":
            raise ArgumentTypeError()
        if v2.val == 0:
            raise InvalidValueError()
        get_var(i.arg1).val = v1.val / v2.val
    else:
        raise InternalError()

def relational(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    get_var(i.arg1).type = "bool"

    if op == "eq" and (v1.type == "nil" or v2.type == "nil"):
        get_var(i.arg1).val = v1.type == v2.type
        return

    if v1.type != v2.type:
        raise ArgumentTypeError()
    if v1.type not in ["int", "string", "bool"]:
        raise ArgumentTypeError()

    if op == "eq":
        get_var(i.arg1).val = v1.val == v2.val
    elif op == "gt":
        get_var(i.arg1).val = v1.val > v2.val
    elif op == "lt":
        get_var(i.arg1).val = v1.val < v2.val
    else:
        raise InternalError()

def and_or(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    if v1.type != "bool" or v2.type != "bool":
        raise ArgumentTypeError()
    
    get_var(i.arg1).type = "bool"
    if   op == "and":
        get_var(i.arg1).val = v1.val and v2.val
    elif op == "or":
        get_var(i.arg1).val = v1.val or  v2.val
    else:
        raise InternalError()

def jump(i: Instruction, op: str):
    lb = i.arg1.val
    if lb not in g.labels:
        raise SemanticCommonError()
    if op == "j":
        g.inst_index = g.labels[lb] # jump
    elif op in {"je", "jne"}:
        v1, v2 = symb(i.arg2), symb(i.arg3)
        if v1.type == "nil" or v2.type == "nil":
            if (v1.type == v2.type) == (op == "je"):
                g.inst_index = g.labels[lb]  # jump
            return
        if v1.type != v2.type:
            raise ArgumentTypeError()
        if (v1.val == v2.val) == (op == "je"):
            g.inst_index = g.labels[lb] # jump

def stack_inst(func, i: Instruction, argc: int):
    i.arg1 = g.stack_var
    if   argc == 1:
        i.arg2 = g.data_stack.pop()
    elif argc == 2:
        i.arg3 = g.data_stack.pop()
        i.arg2 = g.data_stack.pop()
    elif argc == 3:
        raise InternalError("Too many arguments for stack instruction")
    func(i)
    g.data_stack.append(get_var(i.arg1))

# Import here to avoid circular dependency
import instructions as I

def run():
    # Label pass
    for inst in g.instructions:
        if inst.opcode == "label":
            I.ilabel(inst)

    # Main pass
    while g.inst_index < len(g.instructions):
        inst = g.instructions[g.inst_index]
        if inst.opcode == "label":
            g.inst_index += 1
            continue
        try:
            getattr(I, f"i{inst.opcode.lower()}")(inst)
        except IPP23Error:
            raise
        g.inst_index += 1

    return g.exit_code