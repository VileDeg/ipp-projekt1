class Operand:
    def __init__(self, type: str, text: str):
        if type not in ["int", "bool", "string", "nil", "label", "type", "var"]:
            raise Exception("Invalid operand type")

        if type == "int":
            try:
                int(text)
            except Exception as e:
                raise e
        elif type == "bool":
            if text not in ["true", "false"]:
                raise Exception("Invalid bool value")

        self.type = type
        self.text = text

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

class Expression:
    def __init__(self, type: str, value):
        self.type = type
        self.value = value
