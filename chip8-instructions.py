"""
0nnn - SYS addr
Jump to a machine code routine at nnn.

This instruction is only used on the old computers on which Chip-8 was originally implemented. It is ignored by modern interpreters.
"""
def _0nnn_mapper():
    op = (self.opcode & 0xF0FF)
    self.opcode_map.get(op,exit)()


"""
00E0 - CLS
Clear the display.
"""
def _00E0():
    self.display_buffer = [0]*32*64


"""
00EE - RET
Return from a subroutine.

The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.
"""
def _00EE():
    self.pc = self.stack.pop()


"""
1nnn - JP addr
Jump to location nnn.

The interpreter sets the program counter to nnn.
"""
def _1nnn():
    self.pc = self.opcode & 0x0FFF


"""
2nnn - CALL addr
Call subroutine at nnn.

The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC is then set to nnn.
"""
def _2nnn():
    self.stack.append(self.pc)
    self.pc = self.opcode & 0x0FFF


"""
3xkk - SE Vx, byte
Skip next instruction if Vx = kk.

The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
"""
def _3xkk():
    kk = self.opcode & 0x00FF
    if self.registers[vx] == kk:
        self.pc += 2


"""
4xkk - SNE Vx, byte
Skip next instruction if Vx != kk.

The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
"""
def _4xkk():
    kk = self.opcode & 0x00FF
    if self.registers[vx] != kk:
        self.pc += 2 

"""
5xy0 - SE Vx, Vy
Skip next instruction if Vx = Vy.

The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
"""
def _5xy0():
    if self.registers[vx] != self.registers[vy]:
        self.pc += 2 


"""
6xkk - LD Vx, byte
Set Vx = kk.

The interpreter puts the value kk into register Vx.
"""
def _6xkk():
    kk = self.opcode & 0x00FF
    self.registers[vx] = kk


"""
7xkk - ADD Vx, byte
Set Vx = Vx + kk.

Adds the value kk to the value of register Vx, then stores the result in Vx.
"""
def _7xkk():
    kk = self.opcode & 0x00FF
    self.registers[vx] = self.registers[vx] + kk


""" mapping the instructions starting with 8 """

def _8xyn_mapper():
    op = (self.opcode & 0xF00F)
    if op == 0x8000:
        _8xy0()
        return
    self.opcode_map.get(op,exit)()


"""
8xy0 - LD Vx, Vy
Set Vx = Vy.

Stores the value of register Vy in register Vx.
"""
def _8xy0():
    self.registers[vx] = self.registers[vy]

"""
8xy1 - OR Vx, Vy
Set Vx = Vx OR Vy.

Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0.
"""
def _8xy1():
    self.registers[vx] = self.registers[vy] | self.registers[vx]



"""
8xy2 - AND Vx, Vy
Set Vx = Vx AND Vy.

Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND compares the corrseponding bits from two values, and if both bits are 1, then the same bit in the result is also 1. Otherwise, it is 0.
"""
def _8xy2():
    self.registers[vx] = self.registers[vy] & self.registers[vx]


"""
8xy3 - XOR Vx, Vy
Set Vx = Vx XOR Vy.

Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
"""
def _8xy3():
    self.registers[vx] = self.registers[vy] ^ self.registers[vx]


"""
8xy4 - ADD Vx, Vy
Set Vx = Vx + Vy, set VF = carry.

The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
"""
def _8xy4():
    val = self.registers[vy] + self.registers[vx]
    self.registers[0xf] = (val & 0xF00) >> 8
    self.registers[vx] = (val) & 0xFF


"""
8xy5 - SUB Vx, Vy
Set Vx = Vx - Vy, set VF = NOT borrow.

If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
"""
def _8xy5():
    self.registers[vx] = (self.registers[vx] - self.registers[vy]) & 0xFF
    self.registers[0xf] = int(self.registers[vx] > self.registers[vy])


"""
8xy6 - SHR Vx {, Vy}
Set Vx = Vx SHR 1.

If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
"""
def _8xy6():
    self.registers[0xf] = self.registers[vx] & 0x1
    self.registers[vx] = int(self.registers[vx] / 2)


"""
8xy7 - SUBN Vx, Vy
Set Vx = Vy - Vx, set VF = NOT borrow.

If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
"""
def _8xy7():
    self.registers[vx] = (self.registers[vy] - self.registers[vx]) & 0xFF
    self.registers[0xf] = int(self.registers[vy] > self.registers[vx])


"""
8xyE - SHL Vx {, Vy}
Set Vx = Vx SHL 1.

If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
"""
def _8xyE():
    self.registers[0xf] = self.registers[vx] & 0x80
    self.registers[vx] = (self.registers[vx] * 2) & 0xFF



"""
9xy0 - SNE Vx, Vy
Skip next instruction if Vx != Vy.

The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
"""
def _9xy0():
    if self.registers[vx] != self.registers[vy]:
        self.stack.pop()


"""
Annn - LD I, addr
Set I = nnn.

The value of register I is set to nnn.
"""
def _Annn():
    self.index_register = self.opcode & 0x0FFF


"""
Bnnn - JP V0, addr
Jump to location nnn + V0.

The program counter is set to nnn plus the value of V0.
"""
def _Bnnn():
    self.pc = (self.opcode & 0x0FFF) + self.registers[0]



"""
Cxkk - RND Vx, byte
Set Vx = random byte AND kk.

The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.
"""
import random
def _Cxkk():
    r = random.randint(0,255)
    kk = self.opcode & 0x00FF
    self.registers[vx] = r & kk


"""
Dxyn - DRW Vx, Vy, nibble
Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen. See instruction 8xy3 for more information on XOR, and section 2.4, Display, for more information on the Chip-8 screen and sprites.
"""
def _Dxyn2():
    n = self.opcode & 0x000F
    x=self.registers[vx]
    y=self.registers[vy]
    for i in range(n):
        if (y+i) >= 32: y=(y+i)%32
        if x > 64: x=x%64

        row_start_pos = x + y*64
        binary_row = self.get_bin(memory[index_register+i])

        for j in range(8):
            sprite_pixel_value=int(binary_row[j])

            pixel_pos = row_start_pos+j if (row_start_pos+j)%64 == xy%64 else (row_start_pos+j)-64

            self.display_buffer[pixel_pos] = self.display_buffer[pixel_pos] ^ sprite_pixel_value
            self.registers[0xf] = int(not bool(self.display_buffer[pixel_pos]))
def _Dxyn():
    n = self.opcode & 0x000F
    x=self.registers[vx]
    y=self.registers[vy]
    for i in range(n):
        if (y+i) >= 32: y=(y+i)%32
        if x > 64: x=x%64

        binary_row = self.get_bin(memory[index_register+i])

        for j in range(8):
            sprite_pixel_value=int(binary_row[j])

            pixel_pos = x+j
            if pixel_pos >= 64: pixel_pos = (pixel_pos)%64

            self.display_buffer[y][pixel_pos] = self.display_buffer[y][pixel_pos] ^ sprite_pixel_value
            self.registers[0xf] = int(not bool(self.display_buffer[y][pixel_pos]))


""" mapper for Ennn instructions """
def _Exnn_mapper():
    _0nnn_mapper()


"""
Ex9E - SKP Vx
Skip next instruction if key with the value of Vx is pressed.

Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.
"""
def _Ex9E():
    pass


"""
ExA1 - SKNP Vx
Skip next instruction if key with the value of Vx is not pressed.

Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.
"""
def _ExA1():
    pass


""" mapper for Fnnn instructions """
def _Fxnn_mapper():
    _0nnn_mapper()


"""
Fx07 - LD Vx, DT
Set Vx = delay timer value.

The value of DT is placed into Vx.
"""
def _Fx07():
    self.registers[vx] = self.delay_timer_register & 0xFF

"""
Fx0A - LD Vx, K
Wait for a key press, store the value of the key in Vx.

All execution stops until a key is pressed, then the value of that key is stored in Vx.
"""
def _Fx0A():
    pass


"""
Fx15 - LD DT, Vx
Set delay timer = Vx.

DT is set equal to the value of Vx.
"""
def _Fx15():
    self.delay_timer_register = self.registers[vx] & 0xFF


"""
Fx18 - LD ST, Vx
Set sound timer = Vx.

ST is set equal to the value of Vx.
"""
def _Fx18():
    self.sound_timer_register = self.registers[vx] & 0xFF


"""
Fx1E - ADD I, Vx
Set I = I + Vx.

The values of I and Vx are added, and the results are stored in I.
"""
def _Fx1E():
    self.index_register = (self.index_register + self.registers[vx]) & 0xFFFF


"""
Fx29 - LD F, Vx
Set I = location of sprite for digit Vx.

The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
"""
def _Fx29():
    self.index_register = (self.registers[vx]*5) & 0xFFF


"""
Fx33 - LD B, Vx
Store BCD representation of Vx in memory locations I, I+1, and I+2.

The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.
"""
def _Fx33():
    s = "00" + str(self.registers[vx])
    self.memory[self.index_register+2] = int(s[-1]) & 0xF
    self.memory[self.index_register+1] = int(s[-2]) & 0xF
    self.memory[self.index_register] = int(s[-3]) & 0xF


"""
Fx55 - LD [I], Vx
Store registers V0 through Vx in memory starting at location I.

The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
"""
def _Fx55():
    for i in range(vx+1):
        memory[index_register+i] = self.registers[i] & 0xFF


"""
Fx65 - LD Vx, [I]
Read registers V0 through Vx from memory starting at location I.

The interpreter reads values from memory starting at location I into registers V0 through Vx.
"""
def _Fx65():
    for i in range(vx+1):
        self.registers[i] = memory[index_register+i] & 0xFF

