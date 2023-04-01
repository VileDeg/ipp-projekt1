import io
import re
import sys
import xml.etree.ElementTree as et

from interp_classes import *

import error
import globals as g

DEBUG = False

def log(s):
    if DEBUG:
        print(s)
    
def validate_xml(xml_tree: et.ElementTree):
    prog = xml_tree.getroot()
    #log(f"{prog.tag=}")
    if prog.tag != "program":
        error.xmlstruct()
    ra = list(prog.attrib.keys())
    #log(f"{ra=}")
    if not('language' in ra) and prog.attrib['language'] != "IPPcode23": # TODO: description, name
        error.xmlstruct()
    
    for inst in prog:
        #log(f"\t{inst.tag=}")
        if inst.tag != "instruction":
            error.xmlstruct()
        ca = list(inst.attrib.keys())
        #log(f"\t{ca=}")
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

        argc = 1
        for arg in inst:
            #log(f"\t\t{arg.tag=}")
            if argc > 3:
                error.xmlstruct("Too many arguments")
            if arg.tag != "arg"+str(argc):
                error.xmlstruct("Invalid argument tag")
            sa = list(arg.attrib.keys())
            #log(f"\t\t{sa=}")
            if not('type' in sa):
                error.xmlstruct()
                
            arg_type = arg.attrib['type'].lower()
            if arg_type not in ["int", "bool", "string", "nil", "label", "type", "var"]:
                error.xmlstruct("Invalid argument type")

            argc += 1
            
            #log(f"\t\t{arg.text=}")
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

        g.instructions.append(inst_obj)
            
    # check for duplicates in instruction orders
    orders = [i.order for i in g.instructions]
    if len(orders) != len(set(orders)):
        error.xmlstruct("Duplicate instruction order")
    # sort intructions by order
    g.instructions.sort(key=lambda x: x.order)

def initialize(source_file: io.TextIOWrapper):
    g.source_file  = source_file

    try:
        xml_tree = et.parse(g.source_file)
    except:
        error.xmlformat()

    prog = validate_xml(xml_tree)

    fill_instructions(prog)

def get_frame(var: str):
    pref = var[0:2]
    if pref == "TF":
        if g.temp_frame == None:
            error.frame()
        return g.temp_frame
    elif pref == "LF":
        if len(g.frame_stack) == 0:
            error.frame()
        return g.frame_stack[-1]
    elif pref == "GF":
        return g.glob_frame
    else:
        error.frame()
    
def get_var(var: str):
    return get_frame(var)[var[3:]]

def is_var_declared(var: str):
    return var[3:] in get_frame(var)

def is_var_defined(var: str):
    return is_var_declared(var) and get_var(var).value != None

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
        if int(v2.value) == 0:
            error.badval()
        get_var(var).value = int(v1.value) // int(v2.value)
    else:
        error.intern()

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

import instructions as I

def run():
    while g.inst_index < len(g.instructions):
        inst = g.instructions[g.inst_index]
        try:
            getattr(I, "i"+inst.opcode.lower())(inst)
        except Exception:
            raise
        g.inst_index += 1
