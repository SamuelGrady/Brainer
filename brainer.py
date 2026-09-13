from enum import StrEnum

class Instruction(StrEnum):
    NEXT     = '>'
    PREV     = '<'
    ADD      = '+'
    SUB      = '-'
    IN       = ','
    OUT      = '.'
    LOOP_BEG = '['
    LOOP_END = ']'

class Program:
    def __init__(self, raw_program=None, input_handler=None, output_handler=lambda x:print(chr(x),end='')):
        self.instructions = clean_program(raw_program)
        self.length = len(self.instructions or '')
        self.tape = [0]
        self.input_handler = input_handler
        self.output_handler = output_handler
        self.pc = self.dp = 0
        self.stack = []

    def run(self):
        while not self.at_end:
            self.step()

    def step(self):
        i = self.instructions[self.pc]

        if i == Instruction.NEXT:
            self.dp += 1
            if self.dp == len(self.tape): self.tape.append(0) # Make tape larger
        elif i == Instruction.PREV:
            self.dp = max(self.dp-1,0)
        elif i == Instruction.ADD:
            self.tape[self.dp] = (self.tape[self.dp]+1) % 256
        elif i == Instruction.SUB:
            self.tape[self.dp] = (self.tape[self.dp]-1) % 256
        elif i == Instruction.IN:
            if self.input_handler: self.tape[self.dp] = self.input_handler() % 256
        elif i == Instruction.OUT:
            self.output_handler(self.tape[self.dp])
        elif i == Instruction.LOOP_BEG:
            if self.tape[self.dp] == 0:
                added_depth = 0
                while not (self.instructions[self.pc] == Instruction.LOOP_END and added_depth == -1):
                    self.pc += 1
                    if self.instructions[self.pc] == Instruction.LOOP_BEG: added_depth += 1
                    elif self.instructions[self.pc] == Instruction.LOOP_END: added_depth -= 1
            else:
                self.stack.append(self.pc)
        elif i == Instruction.LOOP_END:
            if self.tape[self.dp] == 0:
                self.stack.pop()
            else:
                self.pc = self.stack[-1]

        self.pc += 1

    @property
    def at_end(self):
        return self.pc >= self.length

def clean_program(raw_program):
    if raw_program == None: return None
    instructions = ''
    for line in raw_program.split('\n'):
        for char in (it := iter(line)):
            if char == '#': break # ignore everything after the comments
            if char in Instruction:
                instructions += char
    return instructions