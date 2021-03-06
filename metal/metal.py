# metal.py
#
# One of the main roles of a compiler is taking high-level programs
# such as what you might write in C or Python and reducing them to
# instructions that can execute on actual hardware.
#
# This file implements a very tiny CPU in the form of a Python
# program.  Although simulated, this CPU mimics the behavior of a real
# CPU.  There are registers for performing simple mathematical
# calculations, memory operations for loading/storing values, control
# flow instructions for branching and gotos, and an I/O port for
# performing output.
#
# See the end of this file for some exercises.
#
# The CPU has 8 registers (R0, R1, ..., R7) that hold 32-bit unsigned
# integer values.  Register R0 is hardwired to always contains the
# value 0. Register R7 is initialized to the highest valid memory
# address. A special register PC holds the index of the next
# instruction that will execute.
#
# The memory of the machine consists of 65536 memory slots,
# each of which can hold an integer value.  Special LOAD/STORE
# instructions access the memory.  Instructions are stored
# separately.  All memory addresses from 0-65535 may be used.
#
# The machine has a single I/O port which is mapped to the memory
# address 65535 (0xFFFF).  The symbolic constant IO_OUT contains the
# value 65535 and can be used when writing code.  Writing an integer
# to this address causes the integer value to be printed to terminal.
# This can be useful for debugging.
#
# The machine understands the following instructions--which
# are encoded as tuples:
#
#   ('ADD', 'Ra', 'Rb', 'Rd')       ; Rd = Ra + Rb
#   ('SUB', 'Ra', 'Rb', 'Rd')       ; Rd = Ra - Rb
#   ('INC', 'Ra')                   ; Ra = Ra + 1
#   ('DEC', 'Ra')                   ; Ra = Ra - 1
#   ('AND', 'Ra', 'Rb', 'Rd')       ; Rd = Ra & Rb (bitwise-and)
#   ('OR', 'Ra', 'Rb', 'Rd')        ; Rd = Ra | Rb (bitwise-or)
#   ('XOR', 'Ra', 'Rb', 'Rd')       ; Rd = Ra ^ Rb (bitwise-xor)
#   ('SHL', 'Ra', 'Rb', 'Rd')       ; Rd = Ra << Rb (left bit-shift)
#   ('SHR', 'Ra', 'Rb', 'Rd')       ; Rd = Ra >> Rb (right bit-shift)
#   ('CMP', 'Ra', 'Rb', 'Rd')       ; Rd = (Ra == Rb) (compare)
#   ('CONST', value, 'Rd')          ; Rd = value
#   ('LOAD', 'Rs', 'Rd', offset)    ; Rd = MEMORY[Rs + offset]
#   ('STORE', 'Rs', 'Rd', offset)   ; MEMORY[Rd + offset] = Rs
#   ('JMP', 'Rd', offset)           ; PC = Rd + offset
#   ('BZ', 'Rt', offset)            ; if Rt == 0: PC = PC + offset
#   ('HALT,)                        ; Halts machine
#
# In the the above instructions 'Rx' means some register number such
# as 'R0', 'R1', etc.  The 'PC' register may also be used as a register.
# All memory instructions take their address from register plus an offset
# that's encoded as part of the instruction.
from collections import namedtuple

IO_OUT = 65535
MASK = 0xFFFFFFFF


class Metal:
    def run(self, instructions):
        """
        Run a program. memory is a Python list containing the program
        instructions and other data.  Upon startup, all registers
        are initialized to 0.  R7 is initialized with the highest valid
        memory index (len(memory) - 1).
        """
        self.registers = {f"R{d}": 0 for d in range(8)}
        self.registers["PC"] = 0
        self.instructions = instructions
        self.memory = [0] * 65536
        self.registers["R7"] = len(self.memory) - 2
        self.running = True
        while self.running:
            op, *args = self.instructions[self.registers["PC"]]
            # Uncomment to debug what's happening
            # print(self.registers["PC"], op, self._format_args(args))
            *args, log_fn = args if args and callable(args[-1]) else args + [lambda self: ""]
            self.registers["PC"] += 1
            getattr(self, op)(*args)
            print(log_fn(self), flush=True)
            self.registers["R0"] = 0  # R0 is always 0 (even if you change it)
        return

    def _format_args(self, args):
        formatted = []
        for arg in args:
            if isinstance(arg, str):
                formatted.append(f"{arg}={self.registers[arg]}")
            else:
                formatted.append(str(arg))
        return " ".join(formatted)

    def ADD(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] + self.registers[rb]) & MASK

    def SUB(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] - self.registers[rb]) & MASK

    def INC(self, ra):
        self.registers[ra] = (self.registers[ra] + 1) & MASK

    def DEC(self, ra):
        self.registers[ra] = (self.registers[ra] - 1) & MASK

    def AND(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] & self.registers[rb]) & MASK

    def OR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] | self.registers[rb]) & MASK

    def XOR(self, ra, rb, rd):

        self.registers[rd] = (self.registers[ra] ^ self.registers[rb]) & MASK

    def SHL(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] << self.registers[rb]) & MASK

    def SHR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] >> self.registers[rb]) & MASK

    def CMP(self, ra, rb, rd):
        self.registers[rd] = int(self.registers[ra] == self.registers[rb])

    def CONST(self, value, rd):
        self.registers[rd] = value & MASK

    def LOAD(self, rs, rd, offset):
        self.registers[rd] = (self.memory[self.registers[rs] + offset]) & MASK

    def STORE(self, rs, rd, offset):
        addr = self.registers[rd] + offset
        self.memory[self.registers[rd] + offset] = self.registers[rs]
        if addr == IO_OUT:
            print(self.registers[rs])

    def JMP(self, rd, offset):
        self.registers["PC"] = self.registers[rd] + offset

    def BZ(self, rt, offset):
        if not self.registers[rt]:
            self.registers["PC"] += offset

    def HALT(self):
        self.running = False


Label = namedtuple("Label", ["op", "index"])


# =============================================================================

if __name__ == "__main__":
    machine = Metal()

    # ----------------------------------------------------------------------
    # Program 1:  Computers
    #
    # The CPU of a computer executes low-level instructions.  Using the
    # Metal instruction set above, show how you would compute 3 + 4 - 5
    # and print out the result.
    #

    prog1 = [
        # Set constants, add and store result in R1
        ("CONST", 3, "R1"),
        ("CONST", 4, "R2"),
        ("ADD", "R1", "R2", "R1"),
        # Set constant, add, and store result in R1
        ("CONST", 5, "R2"),
        ("SUB", "R1", "R2", "R1"),
        # Print the result.
        ("STORE", "R1", "R0", IO_OUT),
        ("HALT",),
    ]

    print("PROGRAM 1::: Expected Output: 2")
    machine.run(prog1)
    print(":::PROGRAM 1 DONE")

    # ----------------------------------------------------------------------
    # Problem 2: Computation
    #
    # Write a Metal program that computes 3 * 7.
    #
    # Note: The machine doesn't implement multiplication. So, you need
    # to figure out how to do it.  Hint:  You can use one of the values
    # as a counter.
    LABELS = {
        "LOOP_BEGIN": Label("BZ", 3),
    }
    prog2 = [
        ("CONST", 3, "R1"),  # Counter
        ("CONST", 7, "R2"),  # Increment
        ("CONST", 0, "R3"),  # Running total
        # R3 = 0
        # while True:
        #     if R1 == 0: break
        #     R3 += R2
        #     R1--
        ("BZ", "R1", 3),  # Advance 3 instructions if R1 == 0
        ("ADD", "R3", "R2", "R3"),
        ("DEC", "R1"),
        ("JMP", "R0", LABELS["LOOP_BEGIN"].index),
        # Print result.
        ("STORE", "R3", "R0", IO_OUT),
        ("HALT",),
    ]
    for op, i in LABELS.values():
        assert prog2[i][0] == op

    print("PROGRAM 2::: Expected Output: 21")
    machine.run(prog2)
    print(":::PROGRAM 2 DONE")

    # ----------------------------------------------------------------------
    # Problem 3: Abstraction and functions
    #
    # A major part of programming concerns abstraction. One of the most
    # common tools of abstraction is the concept of a function/procedure.
    # For example, consider this high-level Python code:
    #
    #    def mul(x, y):
    #        result = 0
    #        while x > 0:
    #            result += y
    #            x -= 1
    #        return result
    #
    #    n = 5
    #    result = 1
    #    while n > 0:
    #        result = mul(result, n)
    #        n -= 1
    #
    # How would you encode something like this into machine code?
    # Specifically.  How would you define the function mul(). How
    # would it receive inputs?  How would it return a value?  How
    # would the branching/jump statements work?
    JUMP_TO_END_OFFSET = 3  # n. instructions to advance when breaking out of loop
    LABELS = {
        "LOOP_BEGIN": Label("BZ", 2),
        "FUNCTION_CALL": Label("JMP", 3),
        "FUNCTION_DEF": Label("STORE", 9),
        "LOOP_BEGIN_2": Label("BZ", 12),
    }
    prog3 = [
        ("CONST", 5, "R1"),  # n = 5
        ("CONST", 1, "R2"),  # result = 1
        # while n > 0:
        #     result = mul(result,  n)
        #     n -= 1
        #
        ("BZ", "R1", JUMP_TO_END_OFFSET),  # break if counter == 0
        (
            "JMP",
            "R0",
            LABELS["FUNCTION_DEF"].index,
            lambda self: f"At toplevel: calling mul({self.registers['R2']}, {self.registers['R1']})",
        ),  # call mul function
        (
            "ADD",
            "R0",
            "R6",
            "R2",
            lambda self: f"At toplevel: result = {self.registers['R2']}",
        ),  # Set R2 = return value (R6)
        ("DEC", "R1"),  # R1 -= 1
        ("JMP", "R0", LABELS["LOOP_BEGIN"].index),
        # print(result)
        ("STORE", "R2", "R0", IO_OUT),  # R2 Holds the Result
        ("HALT",),
        # ----------------------------------
        # ; mul(x, y) -> x * y
        #
        #    def mul(x, y):
        #        result = 0
        #        while x > 0:
        #            result += y
        #            x -= 1
        #        return result
        #
        # Arguments are in R2 and R1
        # For the registers we'll write to, copy their contents to memory
        ("STORE", "R2", "R0", 2),
        ("STORE", "R3", "R0", 3),
        ("CONST", 0, "R3"),  # result = 0
        # x = R2
        # y = R1
        ("BZ", "R2", JUMP_TO_END_OFFSET),  # break if x == 0
        (
            "ADD",
            "R3",
            "R1",
            "R3",
            lambda self: f"In mul(): result += y[{self.registers['R1']}]",
        ),  # result += y
        ("DEC", "R2"),  # R2 -= 1
        ("JMP", "R0", LABELS["LOOP_BEGIN_2"].index),
        # Write return value to R6
        ("ADD", "R0", "R3", "R6"),
        # Reinstate the original values for the registers we wrote to, (except for special return
        # value register)
        ("LOAD", "R0", "R2", 2),
        ("LOAD", "R0", "R3", 3),
        ("JMP", "R0", LABELS["FUNCTION_CALL"].index + 1),
    ]
    for op, i in LABELS.values():
        assert prog3[i][0] == op, f"Expected {op} at index {i}, but found {prog2[i][0]}"

    print("PROGRAM 3::: Expected Output: 120")
    machine.run(prog3)
    print(":::PROGRAM 3 DONE")

    # ----------------------------------------------------------------------
    # Problem 4: Ultimate Challenge
    #
    # How would you modify Problem 3 to make a recursive function work?
    #
    #    def mul(x, y):
    #        if x > 0:
    #            return y + mul(x-1, y)
    #        else:
    #            return 0
    #
    #    def fact(n):
    #        if n == 0:
    #            return 1
    #        else:
    #            return mul(n, fact(n-1))
    #
    #    print(fact(5))

    prog4 = [
        # Print result (assumed to be in R1)
        ("STORE", "R1", "R0", IO_OUT),
        ("HALT",),
    ]

    print("PROGRAM 4::: Expected Output: 120")
    machine.run(prog4)
    print(":::PROGRAM 4 DONE")
