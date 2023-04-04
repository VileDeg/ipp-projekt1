from enum import Enum

class Frame(Enum):
    GLOBAL = 1
    LOCAL = 2
    TEMPORARY = 3

class Expression:
    def __init__(self, type: str, val):
        self.type = type
        self.val  = val

def parse_string(s: str):
    i = 0
    l = len(s)
    while i < l:
        c = s[i]
        if c == '\\' and i + 3 < len(s):
            seq = ""
            isseq = True
            j = i + 1
            while j - i < 4:
                cc = s[j]
                if cc not in "0123456789":
                    isseq = False
                    break # Not an escape sequence
                seq += cc
                j += 1
            if isseq:
                s = s[:i] + chr(int(seq)) + s[j:]
                l = len(s) # Update length
        i += 1
    return s

class Operand(Expression):
    def __init__(self, type: str, text: str):
        super().__init__(type, None)
        self.frame = None

        if type == "int":
            try:
                self.val = int(text)
            except Exception:
                raise
        elif type == "float":
            try:
                self.val = float.fromhex(text)
            except Exception:
                try:
                    self.val = float(text)
                except Exception:
                    raise
        elif type == "bool":
            if text == "false":
                self.val = False
            elif text == "true":
                self.val = True
            else:
                raise ValueError("Invalid bool value")
        elif type == "nil":
            self.val = "nil"
        elif type == "var":
            self.val   = text[3:]
            if text.startswith("GF@"):
                self.frame = Frame.GLOBAL
            elif text.startswith("LF@"):
                self.frame = Frame.LOCAL
            elif text.startswith("TF@"):
                self.frame = Frame.TEMPORARY
        elif type == "string":
            self.val = parse_string(text)
        elif type in {"label", "type"}:
            self.val = text
        else:
            raise TypeError("Invalid type")

class Instruction:
    def __init__(self, order: int, opcode: str):
        self.order = order
        self.opcode = opcode
        self.arg1, self.arg2, self.arg3 = None, None, None
    
    def add_operand(self, arg_type: str, value: str):
        if self.arg1 is None:
            self.arg1 = Operand(arg_type, value)
        elif self.arg2 is None:
            self.arg2 = Operand(arg_type, value)
        elif self.arg3 is None:
            self.arg3 = Operand(arg_type, value)
        else:
            raise RuntimeError("Too many operands")

