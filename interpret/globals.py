source_file  = None
instructions = []

frame_stack = []
glob_frame  = {}
temp_frame  = None

labels     = {} # {label_name: instruction}
inst_index = 0

# Insctruction names
opcodes = [
    "move", "createframe", "pushframe", "popframe", "defvar", "call", 
    "return", "pushs", "pops", "add", "sub", "mul", "idiv", "lt", "gt", "eq",
    "and", "or", "not", "int2char", "stri2int", "read", "write", "concat", 
    "strlen", "getchar", "setchar", "type", "label", "jump", "jumpifeq", 
    "jumpifneq", "exit", "dprint", "break"
]