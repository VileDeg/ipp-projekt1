# File with custom exception classes

import sys

class IPP23Error(Exception): # Base class for custom errors
    def __init__(self, message, error_code):
        super().__init__(f"Error: {message}")
        self.error_code = error_code
    def catch(self):
        print(self, file=sys.stderr)
        exit(self.error_code)

class XMLFormatError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"XML format: {message}", 31)

class XMLStructureError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"XML structure: {message}", 32)

class SemanticCommonError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Semantic (label/variable): {message}", 52)

class ArgumentTypeError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Invalid argument type: {message}", 53)

class VariableNotDeclaredError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Variable not declared: {message}", 54)

class InvalidOrEmptyFrameError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Invalid or empty frame: {message}", 55)

class MissingValueError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Missing value: {message}", 56)

class InvalidValueError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Division by zero: {message}", 57)

class StringError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"String: {message}", 58)

class InternalError(IPP23Error):
    def __init__(self, message: str = ""):
        super().__init__(f"Internal: {message}", 99)
