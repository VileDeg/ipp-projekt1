source_file  = None
instructions = []

frame_stack = []
glob_frame  = {}
temp_frame  = None

labels     = {} # {label_name: instruction}
inst_index = 0

# Insctruction names and number of arguments
opcodes = {
    "move" : 2, "createframe" : 0, "pushframe" : 0, "popframe" : 0, 
    "defvar" : 1, "call" : 1, "return" : 0, "pushs" : 1, "pops" : 1, "add" : 3, 
    "sub" : 3, "mul" : 3, "idiv" : 3, "lt" : 3, "gt" : 3, "eq" : 3,
    "and" : 3, "or" : 3, "not" : 3, "int2char" : 2, "stri2int" : 3, "read" : 2, 
    "write" : 1, "concat" : 3, "strlen" : 2, "getchar" : 3, "setchar" : 3, 
    "type" : 2, "label" : 1, "jump" : 1, "jumpifeq" : 3, "jumpifneq" : 3, 
    "exit" : 1, "dprint" : 1, "break" : 0
}