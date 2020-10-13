"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

    def load(self, filename):
        """Load a program into memory."""
        program = []

        with open(f"./examples/{filename}", "r") as f:
            line = f.readline()

            while line:
                line = line.strip()
                if line and line[0] != "#":
                    instruction = line.split("#")[0]
                    instruction = int(instruction, 2)
                    program.append(instruction)
                line = f.readline()

        address = 0

        for instruction in program:
            self.ram_write(address, instruction)
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010

        halted = False

        while not halted:
            instruction = self.ram_read(self.pc)
            arg_nums = ((instruction & 0b11000000) >> 6)
            
            #HLT - HALT
            if instruction == HLT:
                halted = True

            #LDI - LOAD VALUE INTO REGISTER
            elif instruction == LDI:
                reg_num = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)
                self.reg[reg_num] = value

            #PRN - PRINT REGISTER VALUE
            elif instruction == PRN:
                reg_num = self.ram_read(self.pc + 1)
                print(self.reg[reg_num])

            #MUL - MULTIPLY TWO REGISTERS
            elif instruction == MUL:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.alu("MUL", reg_a, reg_b)

            #CATCH UNRECOGNIZED INSTRUCTIONS
            else:
                print("Instruction not recognized")
                sys.exit()

            self.pc += arg_nums + 1

        
