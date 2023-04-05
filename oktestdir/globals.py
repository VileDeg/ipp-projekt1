# File with global variables used by base.py and instructions.py

input_file   = None
source_file  = None
instructions = []

frame_stack = []
glob_frame  = {} # (var_name: Expression)
temp_frame  = None

data_stack = []
stack_var  = None

inst_index   = 0
labels       = {} # (label_name: inst_index)
return_stack = [] # list of inst_index

exit_code = 0

# Insctruction names and number of arguments
opcodes = {
    "move" : 2, "createframe" : 0, "pushframe" : 0, "popframe" : 0, 
    "defvar" : 1, "call" : 1, "return" : 0, "pushs" : 1, "pops" : 1, "add" : 3, 
    "sub" : 3, "mul" : 3, "idiv" : 3, "div" : 3, "lt" : 3, "gt" : 3, "eq" : 3,
    "and" : 3, "or" : 3, "not" : 2, "int2char" : 2, "stri2int" : 3, "read" : 2, 
    "write" : 1, "concat" : 3, "strlen" : 2, "getchar" : 3, "setchar" : 3, 
    "type" : 2, "label" : 1, "jump" : 1, "jumpifeq" : 3, "jumpifneq" : 3, 
    "exit" : 1, "dprint" : 1, "break" : 0, "float2int" : 2, "int2float" : 2,
    # Stack instructions
    "clears" : 0, "adds" : 0, "subs" : 0, "muls" : 0, "idivs" : 0, "divs" : 0, "lts" : 0, 
    "gts" : 0, "eqs" : 0, "ands" : 0, "ors" : 0, "nots" : 0, "int2chars" : 0, 
    "stri2ints" : 0, "jumpifeqs" : 1, "jumpifneqs" : 1, "float2ints" : 0, "int2floats" : 0
}