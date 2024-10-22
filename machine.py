#!/usr/bin/python3
"""Processor model to execute machine code generated for a CISC architecture (von Neumann)."""

import logging
import sys
import time

from isa import Opcode, read_code


from collections import OrderedDict

class DataPath:
    """DataPath handles memory, input/output, and arithmetic operations.

    Implements von Neumann architecture where instructions and data share the same memory space.
    Now includes an LRU cache for memory access.
    """

    def __init__(self, memory_size, input_buffer, cache_size=10):
        self.memory = [0] * memory_size  # Shared memory for both instructions and data
        self.registers = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}  # General-purpose registers
        self.input_buffer = input_buffer  # Input stream
        self.output_buffer = []  # Output stream buffer
        self.cache = OrderedDict()  # LRU Cache
        self.cache_size = cache_size

    def read_from_memory(self, address):
        """Read from memory, using LRU caching mechanism."""
        if address in self.cache:
            # Move the accessed item to the front (most recently used)
            self.cache.move_to_end(address)
            print("cache hit")
            return self.cache[address]
        else:
            print("cache miss")

            # Fetch from memory and add to cache
            data = self.memory[address]
            self._update_cache(address, data)
            return data

    def write_to_memory(self, address, value):
        """Write to memory, updating both memory and cache."""
        self.memory[address] = value
        self._update_cache(address, value)

    def _update_cache(self, address, value):
        """Update the cache with the new address and value."""
        if address in self.cache:
            # If it's already in the cache, just update and move to end
            self.cache.move_to_end(address)
        print("Write-Through to cache")

        self.cache[address] = value

        # If the cache exceeds its size, evict the least recently used item
        if len(self.cache) > self.cache_size:
            print("cache is full delete least used")
            self.cache.popitem(last=False)  # Pop the first item (LRU item)

    def load_register(self, reg, value):
        """Load a value into a register."""
        self.registers[reg] = value

    def add_registers(self, reg1, reg2, result_reg):
        """Add the values of two registers and store the result."""
        self.registers[result_reg] = self.registers[reg1] + self.registers[reg2]

    def subtract_registers(self, reg1, reg2, result_reg):
        """Subtract the value of reg2 from reg1 and store the result."""
        self.registers[result_reg] = self.registers[reg1] - self.registers[reg2]

    def multiply_registers(self, reg1, reg2, result_reg):
        """Multiply the values of two registers and store the result."""
        self.registers[result_reg] = self.registers[reg1] * self.registers[reg2]

    def divide_registers(self, reg1, reg2, result_reg):
        """Divide the value of reg1 by reg2 and store the result."""
        self.registers[result_reg] = self.registers[reg1] // self.registers[reg2]

    def read_input(self):
        """Read input from the input buffer (stream-based)."""
        if len(self.input_buffer) == 0:
            raise EOFError("No more input.")
        return ord(self.input_buffer.pop(0))

    def write_output(self, value):
        """Write output to the output buffer."""
        self.output_buffer.append(chr(value))

    def write_output_number(self, value):
        """Write numeric output to the output buffer."""
        self.output_buffer.append(str(value))  # Append the number directly as a string

    def strcmp(self, str1, str2):
        """Compare two strings (stored in registers) and return 0 if equal."""
        return 0 if str1 == str2 else 1

    def __repr__(self):
        return f"Registers: {self.registers}, Memory: {self.memory[:10]}, Cache: {self.cache}"



class ControlUnit:
    """Control Unit that decodes and executes instructions on the DataPath."""

    def __init__(self, program, data_path):
        # self.cache = None
        self.program = program
        self.data_path = data_path
        self.pc = 0  # Program counter
        self.halted = False

    def fetch_instruction(self):
        """Fetch the current instruction from memory (based on the program counter)."""
        if self.pc >= len(self.program):
            raise StopIteration("Program counter out of bounds.")
        return self.program[self.pc]

    def execute_instruction(self, instr):
        # time.sleep(0.1)
        """Decode and execute the given instruction."""
        opcode = instr["opcode"]
        logging.info(f"Executing: {opcode} at PC={self.pc}")  # Log each instruction execution
        if opcode == Opcode.HALT:
            self.halted = True
            print(self.data_path.cache)
            return

        # Data Transfer Instructions
        elif opcode == Opcode.LOAD:
            reg, addr = instr["arg"].split(", ")
            value = self.data_path.read_from_memory(int(addr, 16))  # Convert addr to int (hex format)
            self.data_path.load_register(reg, value)

        elif opcode == Opcode.STORE:
            reg, addr = instr["arg"].split(", ")
            value = self.data_path.registers[reg]
            self.data_path.write_to_memory(int(addr, 16), value)

        elif opcode == Opcode.CMP:
            reg1, reg2 = str(instr["arg"]).split(", ")

            # Handle cases where the second argument is either a literal, register, or memory reference
            if reg2.isdigit():  # Literal value
                value = int(reg2)
            elif reg2.startswith("[") and reg2.endswith("]"):  # Memory address, e.g., [C]
                mem_addr = reg2[1:-1]  # Extract register or memory address from brackets
                value = self.data_path.read_from_memory(self.data_path.registers[mem_addr])
            else:  # It's a register
                value = self.data_path.registers[reg2]

            # print("reg1 value =",self.data_path.registers[reg1] )
            # print("reg2 value =",value )
            # Compare the value of reg1 with reg2 (or its value)
            result = self.data_path.registers[reg1] - value

            # Set a condition flag (e.g., Zero Flag)
            if result == 0:
                self.data_path.load_register("CMP_FLAG", 1)  # Set CMP_FLAG to 1 if equal (zero flag)
            else:
                self.data_path.load_register("CMP_FLAG", 0)  # Set CMP_FLAG to 0 if not equal

            # print(f"cmp result={result}")



        elif opcode == Opcode.MOV:
            first_arg, second_arg = instr["arg"]
            # if (instr['index']==62):
            #     print("handling 62 now ")
            #     print("second_arg is string= ",isinstance(second_arg, str))

            # Case 1: MOV A, [C] (Memory to Register)
            if isinstance(second_arg, str) and "[" in second_arg and "]" in second_arg:
                reg = second_arg.strip("[]")  # Get the register inside the brackets (C)
                memory_address = self.data_path.registers[reg]  # Get memory address stored in register C
                value = self.data_path.read_from_memory(memory_address)  # Read value from memory
                self.data_path.load_register(first_arg, value)  # Store value in register A

            # Case 2: MOV [B], A (Register/value to Memory)
            elif isinstance(first_arg, str) and "[" in first_arg and "]" in first_arg:
                reg = first_arg.strip("[]")  # Get the register inside the brackets (B)
                memory_address = self.data_path.registers[reg]  # Get memory address stored in register B
                if second_arg.isdigit():
                    self.data_path.write_to_memory(memory_address,second_arg)
                else:
                    value = self.data_path.registers[second_arg]  # Get value from register A
                    self.data_path.write_to_memory(memory_address, value)  # Write value to memory

            # Case 3: MOV A, 87 (Immediate value to Register)
            elif isinstance(second_arg, int):
                self.data_path.load_register(first_arg, second_arg)  # Store the immediate value in register A

            # Case 4: MOV A, B (Register to Register)
            else:
                value = self.data_path.registers[second_arg]  # Get value from register B
                self.data_path.load_register(first_arg, value)  # Store value in register A





        # Arithmetic Instructions
        elif opcode == Opcode.ADD:
            first_arg, second_arg = instr["arg"]

            # Get the value of the first register (destination)
            destination_value = self.data_path.registers[first_arg]

            # Determine if the second argument is a register or an immediate value
            if isinstance(second_arg, int):
                value_to_add = second_arg  # Immediate value to be added
            else:
                value_to_add = self.data_path.registers[second_arg]  # Value from another register

            # Perform the addition
            result = destination_value + value_to_add

            # Store the result back in the first register
            self.data_path.load_register(first_arg, result)


        elif opcode == Opcode.SUB:
            reg1, reg2, result_reg = instr["arg"].split(", ")
            self.data_path.subtract_registers(reg1, reg2, result_reg)

        elif opcode == Opcode.MUL:
            reg1, reg2, result_reg = instr["arg"].split(", ")
            self.data_path.multiply_registers(reg1, reg2, result_reg)

        elif opcode == Opcode.INC:
            # print("increas called")
            if "[" in instr["arg"]:  # Memory location increment
                print("weird")
                address = int(instr["arg"].strip("[]"))  # Extract memory address
                self.data_path.write_to_memory(address, self.data_path.read_from_memory(address) + 1)
            else:  # Register increment

                reg = instr["arg"]
                # print("registe increment =",reg)
                # print("data =",self.data_path.registers[reg])
                self.data_path.load_register(reg, self.data_path.registers[reg] + 1)

        elif opcode == Opcode.DIV:
            first_arg, second_arg = instr["arg"]

            # Get the value of the first register (dividend)
            dividend = self.data_path.registers[first_arg]

            # Determine if the second argument is a register or an immediate value
            if isinstance(second_arg, int):
                divisor = second_arg  # Immediate value as the divisor
            else:
                divisor = self.data_path.registers[second_arg]  # Value from another register

            # Check for division by zero
            if divisor == 0:
                raise ZeroDivisionError(f"Division by zero in instruction {instr}")

            # Perform the division and calculate the remainder
            remainder = dividend % divisor  # Modulus operation to get the remainder
            # Store the remainder back in the first register
            self.data_path.load_register(first_arg, remainder)



    # I/O Operations (Stream-Based)
        elif opcode == Opcode.READ:
            reg = instr["arg"]  # Get the register where the input will be stored

            # Check if there is input left in the input buffer
            if len(self.data_path.input_buffer) == 0:
                 self.data_path.load_register(reg, 0)  # Load 0 to signal EOF (end of input)
            else:
                # Read the next character from the input buffer
                char = self.data_path.input_buffer.pop(0)  # Remove and get the first character
                char_ascii = ord(char)  # Convert the character to its ASCII value

                # Store the ASCII value in the specified register
                self.data_path.load_register(reg, char_ascii)


        elif opcode == Opcode.WRITE:
            reg = instr["arg"]
            value = self.data_path.registers[reg]
            self.data_path.write_output(value)
            # print(f" index = {self.pc} -->{reg} : {value}")

        elif opcode == Opcode.WRITE_NUM:
            reg = instr["arg"]
            value = self.data_path.registers[reg]
            self.data_path.write_output_number(value)  # For numeric output
            # print(f" index = {self.pc} -->{reg} : {value} (as number)")




        # Control Flow
        elif opcode == Opcode.JMP:
            # print("arg og jmp is =",instr["arg"])
            self.pc = instr["arg"] - 1 # Jump to the address

        elif opcode == Opcode.JZ:
            addr = instr["arg"]  # arg is now a tuple with register and address
            # Check if the CMP_FLAG is set (1 means the comparison was zero)
            if self.data_path.registers["CMP_FLAG"] == 1:
                self.pc = addr - 1 # Jump to the given address
            # else:
            #     self.pc += 1  # Move to the next instruction
            #     print("jz ended ,pc is ",self.pc)




        # Complex Instructions (String Support)
        elif opcode == Opcode.STRCMP:
            reg1, reg2 = instr["arg"].split(", ")
            result = self.data_path.strcmp(self.data_path.registers[reg1], self.data_path.registers[reg2])
            self.data_path.load_register("A", result)

        else:
            raise ValueError(f"Unknown opcode: {opcode}")

        if not self.halted:
            self.pc += 1  # Move to the next instruction unless halted

    def run(self, limit=1000):
        """Run the program until HALT or the instruction limit is reached."""
        while not self.halted and self.pc < limit:
            instr = self.fetch_instruction()
            self.execute_instruction(instr)
            logging.debug(f"Executed: {instr}, PC: {self.pc}, DataPath: {self.data_path}")


def simulation(program, input_buffer, memory_size=256, limit=1000):
    """Simulate the execution of the program."""
    data_path = DataPath(memory_size, input_buffer)
    control_unit = ControlUnit(program, data_path)
    control_unit.run(limit)
    return "".join(data_path.output_buffer)


def main(code_file, input_file):
    """Main function to load the machine code and run the simulation."""
    logging.basicConfig(filename="machine/logs/processor.txt", level=logging.INFO, filemode='w')
    program = read_code(code_file)

    with open(input_file, encoding="utf-8") as file:
        input_buffer = [char for char in file.read()]  # Read input into buffer

    output = simulation(program, input_buffer)
    print(f"Output from main: {output}")


if __name__ == "__main__":
    # logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Usage: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
