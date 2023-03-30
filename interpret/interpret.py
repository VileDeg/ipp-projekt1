import re
import argparse
import xml.etree.ElementTree as et
import sys
import os

from interp_classes import *

def open_file(file_name, mode):
    try:
        f = open(file_name, mode, encoding="UTF-8")
    except IOError as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(11)
    return f

def parse_args():
    parser = argparse.ArgumentParser(prog='interpret.py', 
                                    description='Interpreter for IPPcode23. Reads XML from stdin and interprets it.')
    parser.add_argument("--input" , default=sys.stdin, dest="input" , metavar="input_file".upper() ,
                        help="Input stream/file (default: stdin)")
    parser.add_argument("--source", default=sys.stdin, dest="source", metavar="source_file".upper(),
                        help="Source code file (default: stdin)")
    args = parser.parse_args()
    if args.input == sys.stdin and args.source == sys.stdin:
        print("Error: " + "At least one of --input or --source must be specified", file=sys.stderr)
        exit(10)
    return args

def check_xml():
    extxt = "invalid xml"
    try:
        prog = tree.getroot()
        print(f"{prog.tag=}")
        if prog.tag != "program":
            raise Exception(extxt)
        ra = list(prog.attrib.keys())
        print(f"{ra=}")
        if not('language' in ra) and prog.attrib['language'] != "IPPcode23": # TODO: description, name
            raise Exception(extxt)
        
        for inst in prog:
            print(f"\t{inst.tag=}")
            if inst.tag != "instruction":
                raise Exception(extxt)
            ca = list(inst.attrib.keys())
            print(f"\t{ca=}")
            if not('order' in ca) or not('opcode' in ca):
                raise Exception(extxt)
            
            for arg in inst:
                print(f"\t\t{arg.tag=}")
                if not(re.match(r"arg[123]", arg.tag)):
                    raise Exception(extxt)
                sa = list(arg.attrib.keys())
                print(f"\t\t{sa=}")
                if not('type' in sa):
                    raise Exception(extxt)
                
                print(f"\t\t{arg.text=}")
    except BaseException as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(32)

if __name__ == '__main__':
    # Parse arguments
    args = parse_args()
    input_file  = open_file(args.input , "r") if args.input  != sys.stdin else sys.stdin
    source_file = open_file(args.source, "r") if args.source != sys.stdin else sys.stdin

    if args.source != sys.stdin:
        try:
            source_file = open(args.source, "r")
        except IOError as e:
            print("Error: " + str(e), file=sys.stderr)
            exit(11)

    content = source_file.read()
    print(content)
    source_file.seek(0)

    # exit(0)

    # xml load
    try:
        tree = et.parse(source_file)
    except et.ParseError as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(31)
        
    # xml check
    check_xml()    


    exit(0)

    # xml to instruction
    instructions = []
    for inst in prog:
        order = int(inst.attrib['order'])
        opcode = inst.attrib['opcode']
        arg1 = None
        arg2 = None
        arg3 = None
        for arg in inst:
            arg_type = arg.attrib['type']
            value = arg.attrib['value']
            if arg.tag == "arg1":
                arg1 = (arg_type, value)
            elif arg.tag == "arg2":
                arg2 = (arg_type, value)
            elif arg.tag == "arg3":
                arg3 = (arg_type, value)
        instructions.append(Instuction(order, opcode, arg1, arg2, arg3))

    # interpret instructions
    for i in instructions:
        interpret(i)

