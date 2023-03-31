import io
import re
import xml.etree.ElementTree as et

class Argument:
    def __init__(self, arg_type: str, value: str):
        if arg_type not in ["int", "bool", "string", "nil", "label", "type", "var"]:
            raise TypeError("Invalid argument type")
        

        self.arg_type = arg_type
        self.value = value

class Instruction:
    




    def __init__(self, order, opcode):
        self.order = order
        self.opcode = opcode
        self.arg1, self.arg2, self.arg3 = None, None, None
    
    def add_argument(self, arg_type, value):
        try:
            if self.arg1 == None:
                self.arg1 = (arg_type, value)
            elif self.arg2 == None:
                self.arg2 = (arg_type, value)
            elif self.arg3 == None:
                self.arg3 = (arg_type, value)
            else:
                raise Exception("Too many arguments")
        except BaseException:
            raise

class Singleton(type):
    ''' 
    Singleton metaclass.
    Inspired by: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python 
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class Interpreter(metaclass=Singleton):
    def _validate_xml(self, xml_tree: et.ElementTree):
        extxt = "invalid xml"
        try:
            prog = xml_tree.getroot()
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
            return prog
        except BaseException:
            self._error_code = 31
            raise

    def _fill_instructions(self, prog: et.ElementTree):
        for inst in prog:
            order = int(inst.attrib['order'])
            opcode = inst.attrib['opcode']

        try:
            inst_obj = Instruction(order, opcode)

            for arg in inst:
                arg_type = arg.attrib['type']
                value = arg.text
                inst_obj.add_argument(arg_type, value)
        except BaseException:
            self._error_code = 32
            raise

        self._instructions.append(inst_obj)

        # sort intructions by order
        self._instructions.sort(key=lambda x: x.order)
    
    def i_move(self, inst: Instruction):
        pass

    def i_createframe(self, _: Instruction):
        pass

    def i_pushframe(self, _: Instruction):
        pass

    def i_popframe(self, inst: Instruction):
        pass

    def i_defvar(self, inst: Instruction):
        pass
    
    def i_add(self, inst: Instruction):
        pass

    def i_sub(self, inst: Instruction):
        pass

    def i_mul(self, inst: Instruction):
        pass

    def i_idiv(self, inst: Instruction):
        pass

    def i_lt(self, inst: Instruction):
        pass

    def i_gt(self, inst: Instruction):
        pass

    def i_eq(self, inst: Instruction):
        pass

    def i_and(self, inst: Instruction):
        pass

    def i_or(self, inst: Instruction):
        pass

    def i_not(self, inst: Instruction):
        pass

    def i_int2char(self, inst: Instruction):
        pass

    def i_stri2int(self, inst: Instruction):
        pass

    def i_read(self, inst: Instruction):
        pass

    def i_write(self, inst: Instruction):
        pass

    def i_concat(self, inst: Instruction):
        pass

    def i_strlen(self, inst: Instruction):
        pass

    def i_getchar(self, inst: Instruction):
        pass

    def i_setchar(self, inst: Instruction):
        pass

    def i_type(self, inst: Instruction):
        pass

    def i_label(self, inst: Instruction):
        pass

    def i_jump(self, inst: Instruction):
        pass

    def i_jumpifeq(self, inst: Instruction):
        pass

    def i_jumpifneq(self, inst: Instruction):
        pass

    def i_exit(self, inst: Instruction):
        pass

    def i_dprint(self, inst: Instruction):
        pass

    def i_break(self):
        pass

    # def _define_opcodes(self):
    #     self._opcodes = [
    #         "move", "createframe", "pushframe", "popframe", "defvar", "call", "return", "pushs", "pops",
    #         "add", "sub", "mul", "idiv", "lt", "gt", "eq", "and", "or", "not", "int2char", "str2int",
    #         "read", "write", "concat", "strlen", "getchar", "type", "label", "jump", "jumpifeq", "jumpifneq",
    #         "exit", "dprint", "break"
    #     ]

    #     # Assign lambda functions to opcode names
    #     self._idict = {
    #         "move": lambda self, inst: pass
    #     }
    def __init__(self):
        self._source_file  = None
        self._instructions = []
        self._error_code   = 0

    def initialize(self, source_file: io.TextIOWrapper):
        self._source_file  = source_file
        
        #self._opcodes      = []
        #self._idict        = {}

        try:
            xml_tree = et.parse(self._source_file)
        except et.ParseError:
            self._error_code = 31
            raise
        
        try:
            prog = self._validate_xml(xml_tree)
            self._fill_instructions(prog)
        except BaseException:
            raise

    

    @property
    def error_code(self):
        return self.error_code
    
    def run(self):
        for inst in self._instructions:
            getattr(self, f"i_{inst.opcode}")(inst)