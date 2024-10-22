import json
from collections import namedtuple
from enum import Enum


class Opcode(str, Enum):
    """
    Opcode for CISC-based instructions, including both data manipulation and control flow operations.

    The instruction set includes:
    1. Data handling: `LOAD`, `STORE`, `MOV`
    2. Arithmetic operations: `ADD`, `SUB`, `MUL`, `DIV`
    3. Control flow: `JMP`, `JZ`, `CALL`, `RET`
    4. I/O operations: `READ`, `WRITE` (for stream-based I/O)
    5. Complex operations like string manipulation
    """

    # Data Transfer Instructions
    LOAD = "load"  # Load from memory to register
    STORE = "store"  # Store from register to memory
    MOV = "mov"  # Move data between registers

    # Arithmetic Instructions
    ADD = "add"  # Add two registers
    SUB = "sub"  # Subtract one register from another
    MUL = "mul"  # Multiply two registers
    DIV = "div"  # Divide one register by another
    WRITE_NUM = "write_num"  # New opcode for writing numbers

    # Control Flow
    JMP = "jmp"  # Unconditional jump
    JZ = "jz"  # Jump if zero (conditional jump)
    CALL = "call"  # Function call
    RET = "ret"  # Return from function

    # Input/Output Instructions (stream-based)
    READ = "read"  # Read data from I/O stream
    WRITE = "write"  # Write data to I/O stream

    # String Handling (optional for complex tasks)
    STRCMP = "strcmp"  # Compare two strings
    STRCPY = "strcpy"  # Copy a string
    STRLEN = "strlen"  # Get the length of a string
    CMP = "cmp"
    INC = "inc"

    # Halt the machine
    HALT = "halt"

    def __str__(self):
        """Override the default `__str__` to return the string version of the opcode."""
        return str(self.value)


class Term(namedtuple("Term", "line pos symbol")):
    """Represents a term from the source code, linking back to the original instruction."""


def write_code(filename, code):
    """
    Write the machine code to a file as JSON.
    One instruction per line for easier reading and debugging.
    """
    with open(filename, "w", encoding="utf-8") as file:
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(filename):
    """
    Read machine code from a file and convert it back into objects,
    including `Opcode` and `Term` for proper interpretation of instructions.
    """
    with open(filename, encoding="utf-8") as file:
        data = file.read()
        code = json.loads(data)

    for instr in code:
        # Convert string to Opcode
        instr["opcode"] = Opcode(instr["opcode"])

        # Convert term list to Term object
        if "term" in instr:
            assert len(instr["term"]) == 3
            instr["term"] = Term(instr["term"][0], instr["term"][1], instr["term"][2])

    return code

# Example of how to represent machine code in JSON format
# example_code = [
#     {
#         "index": 0,
#         "opcode": "load",
#         "arg": "A, 0x01",  # Load the value from memory address 0x01 into register A
#         "term": [1, 0, "load"]
#     },
#     {
#         "index": 1,
#         "opcode": "add",
#         "arg": "A, B",  # Add the values in register A and B
#         "term": [2, 0, "add"]
#     },
#     {
#         "index": 2,
#         "opcode": "write",
#         "arg": "A",  # Write the value in register A to the output stream
#         "term": [3, 0, "write"]
#     },
#     {
#         "index": 3,
#         "opcode": "halt",
#         "arg": None,
#         "term": [4, 0, "halt"]
#     }
# ]
#
# # Writing and reading code example
# write_code("output.json", example_code)
# code_from_file = read_code("output.json")
