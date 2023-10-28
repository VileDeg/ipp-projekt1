# Parser and interpreter of IPPcode23 language

Documentation of Project Implementation for IPP 2022/2023\
Name and surname: Vadim Goncearenco\
Login: xgonce00

# Parser

## Implementation description
`parse.php` holds `IPPcode23` parser implementation. `parse.php` takes no command line arguments and has a single flag `--help`, that outputs the usage of the script. Script reads the source code from `standart input`.

Implementation uses `XMLWriter` library for generation of `xml-formatted` description of the parsed code. It also makes use of php object-oriented functionality, by defining the classes: `Singleton`, `Parser`, `Token`.
### Classes
`Singleton` - class that solves as an interface to implement the `singleton pattern`. Can't be constructed, holds static reference to all created instanced of child classes.

- `protected constructor` - this class can't be instantiated normally.
- `getInstance` - only way of creating a new instance or retrieving the reference of the only instance.

`Parser` - main class that encapsulates the parser functionality. Derives from `Singleton` as no more then one instance of `Parser` must be created in program.

- `pushToken` - adds new token to array and calls `singleOpcodeOnOneLine` method to resolve some edge-cases.

- `singleOpcodeOnOneLine` - checks if there is only one opcode on the line or if there is an opcode and a label which is named as of opcodes.

- `getTokens` - reads all tokens from the given file and populates internal array of tokens.

`Token` - encapsulates token functionality.

- `constructor` - creates `Token` instance using the given string and calls `testOpcode`.

- `testOpcode` - determines the token's type and in case of opcode, the number and type of arguments.

- `testArgument` - tests the token passed as argument against the list of arguments.

- `isHeader` - checks if token string is `.IPPcode23`.

# Interpreter

## Implementation description
The project implementation is divided into `six` modules:
* `base.py` - central module of the interpreter, holding functions that are commonly used by instructions (`instructions.py`)
* `instructions.py`- module with all the functions implementing instruction functionality, made to be as consise as possible with help of `base.py` functions.
* `classes.py` - holds all the classes implementation in the project.
* `error.py` - custom exception classes to avoid rasing general exceptions (`Exception`) which may lead to hiding bugs and internal errors.
* `globals.py` - module with global variables that are used in `base.py` and `instructions.py`. Separate module for globals provides uniform access to avoid accident redefinition and etc.
* `interpret.py` - project entry point that contains "main" function and command line arguments parsing.

Even though the biggest part of implementation is in global scope, separated in modules, the project still makes use of OOP principles available in Python3, thus there are `three` classes:
* `Expression` - a plain simple class that only has type and value attributes. Used as a record of variable in the corresponding frame and also as base class for `Operand` object.
* `Operand` - class that represent and encapsulates information that belongs to any instruction from source XML file.
    * `__init__` - at creation `Operand` object converts it's value according to `type` attribute. For example parses it's `text` string with `parse_string` function.
* `Instruction` - class hodling an `opcode` string with insctruction name, `order` and up to three arguments of `Operand` type.
    * `add_operand` - adds new argument, while catching or forwading possible exceptions.

Using more classes would gradually increase the amount of code and most likely make it less readable and more cumbersome.

![alt text](interpret/uml.png)