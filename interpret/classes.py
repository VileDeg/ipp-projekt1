from enum import Enum
class Frame(Enum):
    GLOBAL = 1
    LOCAL = 2
    TEMPORARY = 3

class Expression:
    def __init__(self, type: str, val):
        self.type = type
        self.val  = val

class Operand(Expression):
    def __init__(self, type: str, text: str):
        super().__init__(type, None)
        self.frame = None
        
        if type == "int":
            try:
                self.val = int(text)
            except Exception as e:
                raise e
        elif type == "bool":
            if text == "true":
                self.val = True
            elif text == "false":
                self.val = False
            else:
                raise Exception("Invalid bool value")
        elif type == "nil":
            self.val = "nil"
        elif type == "var":
            self.val   = text[3:]
            if   text[0:3] == "GF@":
                self.frame = Frame.GLOBAL
            elif text[0:3] == "LF@":
                self.frame = Frame.LOCAL
            elif text[0:3] == "TF@":
                self.frame = Frame.TEMPORARY
        elif type == "string":
            i = 0
            while i < len(text):
                c = text[i]
                if c == '\\':
                    if i + 3 >= len(text):
                        raise Exception("Invalid escape sequence")
                    seq = ""
                    j = i + 1
                    while j - i < 4:
                        cc = text[j]
                        if cc not in "0123456789":
                            raise Exception("Invalid escape sequence")
                        seq += cc
                        j += 1
                    text = text[:i] + chr(int(seq)) + text[j:]
                i += 1
            self.val = text
        elif type == "label":
            self.val = text
        else:
            raise Exception("Invalid type")

class Instruction:
    def __init__(self, order: int, opcode: str):
        self.order = order
        self.opcode = opcode
        self.arg1, self.arg2, self.arg3 = None, None, None
    
    def add_operand(self, arg_type: str, value: str):
        if self.arg1 == None:
            self.arg1 = Operand(arg_type, value)
        elif self.arg2 == None:
            self.arg2 = Operand(arg_type, value)
        elif self.arg3 == None:
            self.arg3 = Operand(arg_type, value)
        else:
            raise Exception("Too many operands")

