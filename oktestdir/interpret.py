import sys
import argparse

import base # Central module of the interpreter
 
from error import * # Error classes

if __name__ == '__main__':
    # Parse arguments
    try:
        parser = argparse.ArgumentParser(prog='interpret.py', 
                                    description='Interpreter for IPPcode23. Reads XML from stdin and interprets it.')
        parser.add_argument("--input" , default=sys.stdin, dest="input" , metavar="input_file".upper() ,
                            help="Input stream/file (default: stdin)")
        parser.add_argument("--source", default=sys.stdin, dest="source", metavar="source_file".upper(),
                            help="Source code file (default: stdin)")
        args = parser.parse_args()
        if args.input == sys.stdin and args.source == sys.stdin:
            print("Error: At least one of --input or --source must be specified", file=sys.stderr)
            exit(10)
    except SystemExit: # --help flag was used
        exit(0)

    try:    
        input_file  = open(args.input , "r", encoding="UTF-8") if args.input  != sys.stdin else sys.stdin
        source_file = open(args.source, "r", encoding="UTF-8") if args.source != sys.stdin else sys.stdin
    except IOError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        exit(11)

    exit_code = 0 # Exit code of "exit" instruction
    try: # Parse XML and run instructions
        base.initialize(input_file, source_file)
        exit_code = base.run()
    except IPP23Error as e:
        e.catch() # Print error message and exit

    exit(exit_code)