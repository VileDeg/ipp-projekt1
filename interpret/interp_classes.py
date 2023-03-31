import io
import re
import xml.etree.ElementTree as et

DEBUG = False

def log(s):
    if DEBUG:
        log(s)

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

class Operand:
    def __init__(self, type: str, text: str):
        if type not in ["int", "bool", "string", "nil", "label", "type", "var"]:
            raise TypeError("Invalid argument type")

        self.type = type
        self.text = text
 
class Instruction:
    def __init__(self, order: int, opcode: str):
        self.order = order
        self.opcode = opcode
        self.arg1, self.arg2, self.arg3 = None, None, None
    
    def add_operand(self, arg_type: str, value: str):
        try:
            if self.arg1 == None:
                self.arg1 = Operand(arg_type, value)
            elif self.arg2 == None:
                self.arg2 = Operand(arg_type, value)
            elif self.arg3 == None:
                self.arg3 = Operand(arg_type, value)
            else:
                raise Exception("Too many arguments")
        except BaseException:
            raise

class Expression:
    def __init__(self, type: str, value):
        self.type = type
        self.value = value

class FrameStack:
    def __init__(self):
        self._stack      = []
        self._glob_frame = {}
        self._tmp_frame  = {}
    
    def _get_frame(self, var: str):
        pref = var[0:2]
        if pref == "TF":
            return self._tmp_frame
        elif pref == "LF":
            return self._stack[-1]
        elif pref == "GF":
            return self._glob_frame

    def is_var_defined(self, var: str):
        return var[3:] in self._get_frame(var)

    def define_var(self, var: str):
        self._get_frame(var)[var[3:]] = Expression(None, None)

    def set_var_type(self, var: str, type: str):
        self._get_frame(var)[var[3:]].type = type

    def set_var_value(self, var: str, value):
        self._get_frame(var)[var[3:]].value = value

    def get_var_type(self, var: str):
        return self._get_frame(var)[var[3:]].type
    
    def get_var_value(self, var: str):
        return self._get_frame(var)[var[3:]].value
    
    def new_tmp_frame(self):
        self._tmp_frame = {}

    def push_tmp_frame(self):
        self._stack.append(self._tmp_frame)
        self._tmp_frame = {}

    def pop_tmp_frame(self):
        self._tmp_frame = self._stack.pop()

class Interpreter(metaclass=Singleton):
    def __init__(self):
        self._source_file  = None
        self._instructions = []
        self._error_code   = 0

        self._frame_stack  = FrameStack()
    
    def _validate_xml(self, xml_tree: et.ElementTree):
        extxt = "invalid xml"
        try:
            prog = xml_tree.getroot()
            log(f"{prog.tag=}")
            if prog.tag != "program":
                raise Exception(extxt)
            ra = list(prog.attrib.keys())
            log(f"{ra=}")
            if not('language' in ra) and prog.attrib['language'] != "IPPcode23": # TODO: description, name
                raise Exception(extxt)
            
            for inst in prog:
                log(f"\t{inst.tag=}")
                if inst.tag != "instruction":
                    raise Exception(extxt)
                ca = list(inst.attrib.keys())
                log(f"\t{ca=}")
                if not('order' in ca) or not('opcode' in ca):
                    raise Exception(extxt)
                
                for arg in inst:
                    log(f"\t\t{arg.tag=}")
                    if not(re.match(r"arg[123]", arg.tag)):
                        raise Exception(extxt)
                    sa = list(arg.attrib.keys())
                    log(f"\t\t{sa=}")
                    if not('type' in sa):
                        raise Exception(extxt)
                    
                    log(f"\t\t{arg.text=}")
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
                inst_obj.add_operand(arg_type, value)
        except BaseException:
            self._error_code = 32
            raise

        self._instructions.append(inst_obj)

        # sort intructions by order
        self._instructions.sort(key=lambda x: x.order)

    def initialize(self, source_file: io.TextIOWrapper):
        self._source_file  = source_file

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

    def _i_move(self, i: Instruction):
        pass

    def _i_createframe(self, _: Instruction):
        self._frame_stack.new_tmp_frame()

    def _i_pushframe(self, _: Instruction):
        self._frame_stack.push_tmp_frame()

    def _i_popframe(self, _: Instruction):
        self._frame_stack.pop_tmp_frame()

    def _i_defvar(self, i: Instruction):
        self._tmp_frame[i.arg1.text] = Expression(i.arg1.type, None)
    
    def __get_var_val(self, var: str):
        if not self._frame_stack.is_var_defined(var):
            return None
        return self._frame_stack.get_var_value(var)

    def __var_symb_symb(self, i: Instruction):
        if self.__get_var_val(i.arg1.text) == None:
            raise Exception("Variable not defined")
        
        v1 = Expression(i.arg2.type, i.arg2.text)
        v2 = Expression(i.arg3.type, i.arg3.text)

        if i.arg2.type == "var":
            v1 = self.__get_var_val(i.arg2.text)

        if i.arg3.type == "var":
            v2 = self.__get_var_val(i.arg3.text)

        return v1, v2

    def __arithm(self, i: Instruction, op: str):
        v1, v2 = self.__var_symb_symb(i)
        
        if v1.type != "int" or v2.type != "int":
            raise Exception("Invalid argument type")

        varname = i.arg1.text
        self._frame_stack.set_var_type(varname, "int")
        if   op == "add":
            self._frame_stack.set_var_value(varname, int(v1.value) + int(v2.value))
        elif op == "sub":
            self._frame_stack.set_var_value(varname, int(v1.value) - int(v2.value))
        elif op == "mul":
            self._frame_stack.set_var_value(varname, int(v1.value) * int(v2.value))
        elif op == "idiv":
            self._frame_stack.set_var_value(varname, int(v1.value) // int(v2.value))
        else:
            raise Exception("Invalid operation")
    
    def __relational(self, i: Instruction, op: str):
        v1, v2 = self.__var_symb_symb(i)

        if v1.type != v2.type:
            raise Exception("Invalid argument type")
        
        varname = i.arg1.text
        if   op == "lt":
            self._tmp_frame[varname].value = int(v1.value) < int(v2.value)
        elif op == "gt":
            self._tmp_frame[varname].value = int(v1.value) > int(v2.value)
        elif op == "eq":
            self._tmp_frame[varname].value = int(v1.value) == int(v2.value)
        else:
            raise Exception("Invalid operation")

    def _i_add(self, i: Instruction):
        self.__arithm(i, "add")

    def _i_sub(self, i: Instruction):
        self.__arithm(i, "sub")

    def _i_mul(self, i: Instruction):
        self.__arithm(i, "mul")

    def _i_idiv(self, i: Instruction):
        self.__arithm(i, "idiv")

    def _i_lt(self, i: Instruction):
        self.__relational(i, "lt")

    def _i_gt(self, i: Instruction):
        self.__relational(i, "gt")

    def _i_eq(self, i: Instruction):
        self.__relational(i, "eq")

    def _i_and(self, i: Instruction):
        pass

    def _i_or(self, i: Instruction):
        pass

    def _i_not(self, i: Instruction):
        pass

    def _i_int2char(self, i: Instruction):
        pass

    def _i_stri2int(self, i: Instruction):
        pass

    def _i_read(self, i: Instruction):
        pass

    def _i_write(self, i: Instruction):
        pass

    def _i_concat(self, i: Instruction):
        pass

    def _i_strlen(self, i: Instruction):
        pass

    def _i_getchar(self, i: Instruction):
        pass

    def _i_setchar(self, i: Instruction):
        pass

    def _i_type(self, i: Instruction):
        pass

    def _i_label(self, i: Instruction):
        pass

    def _i_jump(self, i: Instruction):
        pass

    def _i_jumpifeq(self, i: Instruction):
        pass

    def _i_jumpifneq(self, i: Instruction):
        pass

    def _i_exit(self, i: Instruction):
        pass

    def _i_dlog(self, i: Instruction):
        pass

    def _i_break(self):
        pass


    @property
    def error_code(self):
        return self._error_code
    
    def run(self):
        for inst in self._instructions:
            try:
                getattr(self, f"_i_{inst.opcode.lower()}")(inst)
            except BaseException:
                raise