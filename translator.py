#!/usr/bin/python3
"""Translator for Asm to machine code for a CISC architecture."""

import sys
from isa import Opcode, Term, write_code


def get_meaningful_token(line):
    """
    Extract meaningful tokens (labels or instructions) from the line.
    Remove comments and extra spaces.
    """
    return line.split(";", 1)[0].split("#", 1)[0].strip()


def translate_stage_1(text):
    """
    First pass of the translator. Convert the program text into a list of instructions
    and determine label addresses.

    In your case (CISC), instructions may contain labels and complex operands. Labels
    are stored in a dictionary for later replacement with actual addresses.
    """
    code = []
    labels = {}

    for line_num, raw_line in enumerate(text.splitlines(), 1):
        token = get_meaningful_token(raw_line)
        if token == "":
            continue

        pc = len(code)  # Program counter representing the current instruction address

        if token.endswith(":"):  # Handle labels
            label = token.strip(":")
            assert label not in labels, "Redefinition of label: {}".format(label)
            labels[label] = pc
        elif " " in token:  # Handle instructions with operands (e.g., `LOAD A, 0x01`)
            sub_tokens = token.split(" ")
            mnemonic = sub_tokens[0].lower()
            arg = " ".join(sub_tokens[1:])  # Allows more complex operands like `A, 0x01`
            opcode = Opcode(mnemonic)
            code.append({"index": pc, "opcode": opcode, "arg": arg, "term": Term(line_num, 0, token)})
        else:  # Handle instructions without operands (e.g., `HALT`)
            opcode = Opcode(token.lower())
            code.append({"index": pc, "opcode": opcode, "term": Term(line_num, 0, token)})
    # print(f"Generated code so far: {code}")  # Add this line to print generated instructions

    return labels, code


def translate_stage_2(labels, code):
    """
    Second pass of the translator. Replace label references in the arguments
    with the actual addresses they correspond to, and handle different MOV cases.
    """
    for instruction in code:
        if "arg" in instruction and isinstance(instruction["arg"], str):
            if instruction["opcode"] in {Opcode.WRITE,Opcode.WRITE_NUM, Opcode.READ, Opcode.INC, Opcode.CMP, Opcode.HALT}:
               continue
            # print(instruction)
            # Check if the argument contains both a register and a label or immediate value
            if ", " in instruction["arg"]:
                # Split the argument into two parts
                first_arg, second_arg = instruction["arg"].split(", ")

                # Case 1: MOV A, [C]
                if "[" in second_arg and "]" in second_arg:
                    mem_address = second_arg  # Keep memory reference as it is
                    instruction["arg"] = (first_arg, mem_address)

                # Case 2: MOV [B], A
                elif "[" in first_arg and "]" in first_arg:
                    mem_address = first_arg  # Keep memory reference as it is
                    instruction["arg"] = (mem_address, second_arg)

                # Case 3: MOV A, 87 (Immediate value)
                elif second_arg.isdigit():
                    instruction["arg"] = (first_arg, int(second_arg))  # Store as tuple (reg, immediate value)

                elif second_arg.isalpha() and len(second_arg) == 1:
                      instruction["arg"] = (first_arg, second_arg)
                # Handling if second argument is a label (like a jump target)
                else:
                    if second_arg in labels:
                        instruction["arg"] = (first_arg, labels[second_arg])  # Store as tuple (reg, address)
                    else:
                        raise ValueError(f"Label not defined: {second_arg}")

            else:
                # If it's just a label without a register (for jumps), replace the label with its address
                label = instruction["arg"]
                if label in labels:
                    instruction["arg"] = labels[label]
                else:
                    raise ValueError(f"Label not defined: {label}")
    # print(code)
    return code



def translate(text):
    """
    Translate assembly code text into machine code in two stages:
    1. First, identify labels and instructions.
    2. Second, replace label arguments with addresses.
    """
    labels, code = translate_stage_1(text)
    code = translate_stage_2(labels, code)
    return code


def main(source, target):
    """Entry function for the translator. Parameters are the source asm file and the target output file."""
    with open(source, encoding="utf-8") as f:
        source_code = f.read()

    # Translate the source code into machine code
    machine_code = translate(source_code)

    # Write the machine code to the target file
    write_code(target, machine_code)

    print(f"Source Lines of Code: {len(source_code.splitlines())}")
    print(f"Number of Instructions: {len(machine_code)}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: translator.py <input_file> <output_file>"
    _, source_file, target_file = sys.argv
    main(source_file, target_file)
