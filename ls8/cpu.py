"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.operations = {}
        self.fl = 0b00000000
        self.running = False

        self.operations[0b00000001] = self.handleHLT
        self.operations[0b10000010] = self.handleLDI
        self.operations[0b01000111] = self.handlePRN
        self.operations[0b10100010] = self.handleMUL
        self.operations[0b10100011] = self.handleDIV
        self.operations[0b10100000] = self.handleADD
        self.operations[0b10100001] = self.handleSUB
        self.operations[0b01000101] = self.handlePUSH
        self.operations[0b01000110] = self.handlePOP
        self.operations[0b01010000] = self.handleCALL
        self.operations[0b00010001] = self.handleRET
        self.operations[0b10100111] = self.handleCMP
        self.operations[0b01010100] = self.handleJMP
        self.operations[0b01010101] = self.handleJEQ
        self.operations[0b01010110] = self.handleJNE
        self.operations[0b10101000] = self.handleAND
        self.operations[0b10101010] = self.handleOR
        self.operations[0b10101011] = self.handleXOR
        self.operations[0b01101001] = self.handleNOT
        self.operations[0b10101100] = self.handleSHL
        self.operations[0b10101101] = self.handleSHR
        self.operations[0b10100100] = self.handleMOD

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
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            if self.reg[reg_b] == 0:
                print("Cannot divide by zero. Exiting...")
                self.running = False
            else:
                self.reg[reg_a] //= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
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
        self.running = True

        while self.running:
            instruction = self.ram_read(self.pc)
            arg_nums = (instruction & 0b11000000) >> 6
            pc_already_moved = (instruction & 0b00010000) >> 4

            if instruction in self.operations:
                self.operations[instruction]()

            else:
                print(f"Instruction {instruction} not recognized")
                sys.exit(1)

            if not pc_already_moved:
                self.pc += arg_nums + 1

    #ADD - ADD TWO REGISTERS
    def handleADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_a, reg_b)

    #AND - BITWISE AND TWO REGISTERS
    def handleAND(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("AND", reg_a, reg_b)

    #CALL - CALL A SUBROUTINE
    def handleCALL(self):
        reg_num = self.ram_read(self.pc + 1)
        next_address = self.pc + 2
        self.reg[7] -= 1
        self.ram_write(self.reg[7], next_address)
        self.pc = self.reg[reg_num]

    #CMP - COMPARE VALUES OF TWO REGISTERS
    def handleCMP(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        operand_a = self.reg[reg_a]
        operand_b = self.reg[reg_b]

        if operand_a == operand_b:
            self.fl = 0b00000001
        elif operand_a > operand_b:
            self.fl = 0b00000010
        else:
            self.fl = 0b00000100

    #DIV - DIVIDE REG_A BY REG_B
    def handleDIV(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("DIV", reg_a, reg_b)

    #HLT - HALT
    def handleHLT(self):
        self.running = False

    #JEQ - JUMP TO AN ADDRESS IF E FLAG IS TRUE
    def handleJEQ(self):
        if self.fl == 1:
            reg_num = self.ram_read(self.pc + 1)
            addr_to_jump_to = self.reg[reg_num]
            self.pc = addr_to_jump_to
        else:
            self.pc += 2

    #JMP - JUMP TO AN ADDRESS
    def handleJMP(self):
        reg_num = self.ram_read(self.pc + 1)
        addr_to_jump_to = self.reg[reg_num]
        self.pc = addr_to_jump_to

    #JNE - JUMP TO AN ADDRESS IF E FLAG IS FALSE
    def handleJNE(self):
        if self.fl != 1:
            reg_num = self.ram_read(self.pc + 1)
            addr_to_jump_to = self.reg[reg_num]
            self.pc = addr_to_jump_to
        else:
            self.pc += 2

    #LDI - LOAD VALUE INTO REGISTER
    def handleLDI(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value

    #MOD - MOD TWO REGISTERS
    def handleMOD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MOD", reg_a, reg_b)

    #MUL - MULTIPLY TWO REGISTERS
    def handleMUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_a, reg_b)

    #NOT - BITWISE NOT A REGISTER
    def handleNOT(self):
        reg_a = self.ram_read(self.pc + 1)
        self.alu("NOT", reg_a, None)

    #OR - BITWISE OR TWO REGISTERS
    def handleOR(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("OR", reg_a, reg_b)

    #POP - POP A VALUE OFF THE STACK AND INTO A REGISTER
    def handlePOP(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.reg[7])
        self.reg[7] += 1
        self.reg[reg_num] = value

    #PRN - PRINT REGISTER VALUE
    def handlePRN(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])

    #PUSH - PUSH A VALUE INTO THE STACK 
    def handlePUSH(self):
        reg_num = self.ram_read(self.pc + 1)
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.reg[reg_num])

    #RET - RETURN FROM A SUBROUTINE
    def handleRET(self):
        resume_address = self.ram_read(self.reg[7])
        self.reg[7] += 1
        self.pc = resume_address

    #SHL - LEFT SHIFT REG_A BY REB_B
    def handleSHL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("SHL", reg_a, reg_b)

    #SHR - RIGHT SHIFT REG_A BY REB_B
    def handleSHR(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("SHR", reg_a, reg_b)

    #SUB - SUBTRACT REG_A FROM REG_B
    def handleSUB(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("SUB", reg_a, reg_b)

    #XOR - BITWISE XOR TWO REGISTERS
    def handleXOR(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("XOR", reg_a, reg_b)
        
