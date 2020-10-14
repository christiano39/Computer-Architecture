"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.operations = {}
        self.running = False
        self.sp = 255

        self.operations[0b00000001] = self.handleHLT
        self.operations[0b10000010] = self.handleLDI
        self.operations[0b01000111] = self.handlePRN
        self.operations[0b10100010] = self.handleMUL
        self.operations[0b10100000] = self.handleADD
        self.operations[0b01000101] = self.handlePUSH
        self.operations[0b01000110] = self.handlePOP
        self.operations[0b01010000] = self.handleCALL
        self.operations[0b00010001] = self.handleRET

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

    #HLT - HALT
    def handleHLT(self):
        self.running = False

    #LDI - LOAD VALUE INTO REGISTER
    def handleLDI(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value

    #PRN - PRINT REGISTER VALUE
    def handlePRN(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])

    #MUL - MULTIPLY TWO REGISTERS
    def handleMUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_a, reg_b)

    #ADD - ADD TWO REGISTERS
    def handleADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_a, reg_b)

    #PUSH - PUSH A VALUE INTO THE STACK 
    def handlePUSH(self):
        reg_num = self.ram_read(self.pc + 1)
        self.sp -= 1
        self.ram_write(self.sp, self.reg[reg_num])

    #POP - POP A VALUE OFF THE STACK AND INTO A REGISTER
    def handlePOP(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.sp)
        self.sp += 1
        self.reg[reg_num] = value

    #CALL - CALL A SUBROUTINE
    def handleCALL(self):
        reg_num = self.ram_read(self.pc + 1)
        next_address = self.pc + 2
        self.sp -= 1
        self.ram_write(self.sp, next_address)
        self.pc = self.reg[reg_num] - 2

    #RET - RETURN FROM A SUBROUTINE
    def handleRET(self):
        resume_address = self.ram_read(self.sp)
        self.sp += 1
        self.pc = resume_address - 1

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            instruction = self.ram_read(self.pc)
            arg_nums = ((instruction & 0b11000000) >> 6)

            if instruction in self.operations:
                self.operations[instruction]()

            else:
                print(f"Instruction {instruction} not recognized")
                sys.exit(1)

            self.pc += arg_nums + 1

        
