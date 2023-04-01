import sys
import argparse

import base

def open_file(file_name: str, mode: str):
    try:
        f = open(file_name, mode, encoding="UTF-8")
    except IOError:
        raise
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
        raise Exception("At least one of --input or --source must be specified")
    return args

if __name__ == '__main__':
    # Parse arguments
    try:
        args = parse_args()
    except BaseException as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(10)

    try:    
        input_file  = open_file(args.input , "r") if args.input  != sys.stdin else sys.stdin
        source_file = open_file(args.source, "r") if args.source != sys.stdin else sys.stdin
    except BaseException as e:
        print("Error: " + str(e), file=sys.stderr)
        exit(11)

    try:
        base.initialize(source_file)
        base.run()
    except BaseException as e:
        print("Error: " + str(e), file=sys.stderr)
        #print(interp.error.code, file=sys.stderr)
        exit(base.error.code)
    