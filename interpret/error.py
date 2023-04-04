import sys

code = 0
g = sys.modules[__name__]

class IPPError(Exception):
    def __init__(self, message, error_code):
        super().__init__(f"Error: {message}")
        self.error_code = error_code
    def catch(self):
        print(self, file=sys.stderr)
        exit(self.error_code)

class CLAError(IPPError):
    def __init__(self, message):
        super().__init__(f"Command line arguments: {message}", 10)

class XMLFormatError(IPPError):
    def __init__(self, message):
        super().__init__(f"XML format: {message}", 31)

class XMLStructureError(IPPError):
    def __init__(self, message):
        super().__init__(f"XML structure: {message}", 32)

class SemanticBaseError(IPPError):
    def __init__(self, message):
        super().__init__(f"Semantic (label/variable): {message}", 52)

class ArgumentTypeError(IPPError):
    def __init__(self, message):
        super().__init__(f"Invalid argument type: {message}", 53)

class VariableNotDeclaredError(IPPError):
    def __init__(self, message):
        super().__init__(f"Variable not declared: {message}", 54)

class InvalidOrEmptyFrameError(IPPError):
    def __init__(self, message):
        super().__init__(f"Invalid or empty frame: {message}", 55)

class MissingValueError(IPPError):
    def __init__(self, message):
        super().__init__(f"Missing value: {message}", 56)

class DivisionByZeroError(IPPError):
    def __init__(self, message):
        super().__init__(f"Division by zero: {message}", 57)

class StringError(IPPError):
    def __init__(self, message):
        super().__init__(f"String: {message}", 58)


def xmlformat(txt: str = ""):
    g.code = 31
    raise Exception("XML format: " + txt)

def xmlstruct(txt: str = ""):
    g.code = 32
    raise Exception("XML structure: " + txt)

def sembase(txt: str = ""):
    g.code = 52
    raise Exception("Semantic (label/variable): " + txt)

def argtype(txt: str = ""):
    g.code = 53
    raise Exception("Invalid argument type: " + txt)

def novar(txt: str = ""):
    g.code = 54
    raise Exception("Variable not declared: " + txt)

def frame(txt: str = ""):
    g.code = 55
    raise Exception("Invalid or empty frame: " + txt)

def noval(txt: str = ""):
    g.code = 56
    raise Exception("Missing value: " + txt)

def badval(txt: str = ""):
    g.code = 57
    raise Exception("Division by zero: " + txt)

def badstr(txt: str = ""):
    g.code = 58
    raise Exception("String: " + txt)

def intern(txt: str = ""):
    g.code = 99
    raise Exception("Internal: " + txt)