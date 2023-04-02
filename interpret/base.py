import io
import re
import sys
import xml.etree.ElementTree as et

from classes import *

import error
import globals as g

DEBUG = False

def log(s):
    if DEBUG:
        print(s)

def parse_xml(xml_tree: et.ElementTree):
    prog = xml_tree.getroot()
    if prog.tag != "program":
        error.xmlstruct()
    ra = list(prog.attrib.keys())
    # TODO: description, name?
    if not('language' in ra) and prog.attrib['language'] != "IPPcode23":
        error.xmlstruct()
    
    for inst in prog:
        if inst.tag != "instruction":
            error.xmlstruct()
        ca = list(inst.attrib.keys())
        if not('order' in ca) or not('opcode' in ca):
            error.xmlstruct()
        try:
            order = int(inst.attrib['order'])
        except:
            error.xmlstruct("Order is not an integer")
        if order < 1:
            error.xmlstruct("Invalid instruction order")

        opcode = inst.attrib['opcode'].lower()
        if opcode not in g.opcodes:
            error.xmlstruct("Invalid opcode")

        # create instruction object
        inst_obj = Instruction(order, opcode)

        arglist = []
        argc = 1
        for arg in inst:
            if argc > g.opcodes[opcode]:
                error.xmlstruct("Too many arguments")
            if not re.match(r"arg[1-3]", arg.tag):
                error.xmlstruct("Invalid argument tag")
            sa = list(arg.attrib.keys())
            if not('type' in sa):
                error.xmlstruct()
                
            arg_type = arg.attrib['type'] #.lower()
            if arg_type not in ["int", "float", "bool", "string", "nil", "label", "type", "var"]:
                error.xmlstruct("Invalid argument type")

            arglist.append((arg_type, arg.text, int(arg.tag[3])))

            argc += 1
        if argc - 1 < g.opcodes[opcode]:
            error.xmlstruct("Too few arguments")

        arglist.sort(key=lambda x: x[2])

        argc = 1
        for triple in arglist:
            if triple[2] != argc:
                error.xmlstruct("Invalid argument order")
            # add operand to instruction
            try:
                inst_obj.add_operand(triple[0], triple[1])
            except Exception as e:
                error.xmlstruct(str(e))            
            argc += 1
        # add instruction to list
        g.instructions.append(inst_obj)
    
    # check for duplicates in instruction orders
    orders = [i.order for i in g.instructions]
    if len(orders) != len(set(orders)):
        error.xmlstruct("Duplicate instruction order")
    # sort intructions by order
    g.instructions.sort(key=lambda x: x.order)

def initialize(input_file: io.TextIOWrapper, source_file: io.TextIOWrapper):
    g.input_file  = input_file
    g.source_file = source_file

    try:
        xml_tree = et.parse(g.source_file)
    except:
        error.xmlformat()

    parse_xml(xml_tree)

def get_frame(op: Operand):
    if   op.frame == Frame.TEMPORARY:
        if g.temp_frame == None:
            error.frame()
        return g.temp_frame
    elif op.frame == Frame.LOCAL:
        if len(g.frame_stack) == 0:
            error.frame()
        return g.frame_stack[-1]
    elif op.frame == Frame.GLOBAL:
        return g.glob_frame
    else:
        error.intern()
    
def get_var(op: Operand):
    return get_frame(op)[op.val]

def is_var_declared(op: Operand):
    return op.val in get_frame(op)

def is_var_defined(op: Operand):
    return is_var_declared(op) and get_var(op).val != None

def get_var_if_def(op: Operand):
    if not is_var_defined(op):
        error.novar()
    return get_var(op)

def symb(op: Operand):
    if op.type == "var":
        return get_var_if_def(op)
    else:
        return Expression(op.type, op.val)

def var_symb(i: Instruction):
    if not is_var_declared(i.arg1):
        error.novar()
    
    v1 = symb(i.arg2)

    return v1

def var_symb_symb(i: Instruction):
    v1 = var_symb(i)
    v2 = symb(i.arg3)

    return v1, v2

def arithm(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)
    
    if v1.type != v2.type:
        error.argtype()
    if v1.type != "int" or v1.type != "float":
        error.argtype()

    get_var(i.arg1).type = v1.type
    if   op == "add":
        get_var(i.arg1).val = v1.val + v2.val
    elif op == "sub":
        get_var(i.arg1).val = v1.val - v2.val
    elif op == "mul":
        get_var(i.arg1).val = v1.val * v2.val
    elif op == "idiv":
        if v1.type != "int":
            error.argtype()
        if v2.val == 0:
            error.badval()
        get_var(i.arg1).val = v1.val // v2.val
    elif op == "div":
        if v1.type != "float":
            error.argtype()
        if v2.val == 0:
            error.badval()
        get_var(i.arg1).val = v1.val / v2.val
    else:
        error.intern()

def relational(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    if v1.type != v2.type:
        error.argtype()
    if v1.type != "int" and v1.type != "string" and v1.type != "bool":
        error.argtype()
    
    if   op == "lt":
        get_var(i.arg1).val = v1.val < v2.val
    elif op == "gt":
        get_var(i.arg1).val = v1.val > v2.val
    elif op == "eq":
        get_var(i.arg1).val = v1.val == v2.val
    else:
        error.intern()

def and_or(i: Instruction, op: str):
    v1, v2 = var_symb_symb(i)

    if v1.type != "bool" or v2.type != "bool":
        error.argtype()
    
    if   op == "and":
        get_var(i.arg1).val = v1.val and v2.val
    elif op == "or":
        get_var(i.arg1).val = v1.val or  v2.val
    else:
        error.intern()

import instructions as I

def label_pass():
    for inst in g.instructions:
        if inst.opcode == "label":
            I.ilabel(inst)

def run():
    label_pass()

    while g.inst_index < len(g.instructions):
        inst = g.instructions[g.inst_index]
        if inst.opcode == "label":
            g.inst_index += 1
            continue

        try:
            getattr(I, "i"+inst.opcode.lower())(inst)
        except Exception:
            raise
        g.inst_index += 1

    return error.code