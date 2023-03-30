class Argument:
    def __init__(self, arg_type, value):
        self.arg_type = arg_type
        self.value = value

class Instuction:
    def __init__(self, order, opcode, arg1, arg2, arg3):
        self.order = order
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
    
    def add_argument(self, arg_type, value):
        if self.arg1 == None:
            self.arg1 = (arg_type, value)
        elif self.arg2 == None:
            self.arg2 = (arg_type, value)
        elif self.arg3 == None:
            self.arg3 = (arg_type, value)
        else:
            raise Exception("Too many arguments")
