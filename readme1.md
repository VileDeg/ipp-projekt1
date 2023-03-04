Documentation of Project Implementation for IPP 2022/2023\
Name and surname: Vadim Goncearenco\
Login: xgonce00

# Implementation description
`parse.php` holds `IPPcode23` parser implementation. `parse.php` takes no command line arguments and has a single flag `--help`, that outputs the usage of the script. Script reads the source code from `standart input`.

Implementation uses `XMLWriter` library for generation of `xml-formatted` description of the parsed code. It also makes use of php object-oriented functionality, by defining the classes: `Singleton`, `Parser`, `Token`.
## Classes
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
