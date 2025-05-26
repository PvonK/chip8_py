import curses
import datetime
import time
import random

class Chip8():
    def __init__(self):
        # Input
        self.key_inputs = [0] * 16
        self.pressed_key = None
        # Output
        self.display_buffer = [[0 for j in range(64)] for i in range(32)]
        #self.display_buffer = [0]*32*64
        # CPU
        self.registers = [0 for i in range(16)]
        self.sound_timer_register = 0
        self.delay_timer_register = 0
        self.index_register = 0
        self.stack = []
        self.opcode = 0
        self.pc = 0
        self.vx = 0
        self.vy = 0
        # Memory
        self.memory = [0] * 4096
        self.memory_offset = 0x200
        self.increment=2

        self.logfile = open("logfile.txt","a")

        self.key_mapping = {

            ord("1"):0x1 , ord("2"):0x2 , ord("3"):0x3 , ord("4"):0xC,
            ord("q"):0x4 , ord("w"):0x5 , ord("e"):0x6 , ord("r"):0xD,
            ord("a"):0x7 , ord("s"):0x8 , ord("d"):0x9 , ord("f"):0xE,
            ord("z"):0xA , ord("x"):0x0 , ord("c"):0xB , ord("v"):0xF,

            }



    # methods

    def log(self, l):
        #print(l)
        self.logfile.write("["+str(datetime.datetime.now())+"]"+ l + "\n")

    def init(self):
        self.log("running init...")
        # Input
        self.key_inputs = [0] * 16
        # Output
        self.display_buffer = [[0 for j in range(64)] for i in range(32)]

        # CPU
        self.registers = [0 for i in range(16)]
        self.sound_timer_register = 0
        self.delay_timer_register = 0
        self.index_register = 0
        self.stack = []
        self.opcode = 0
        # Memory
        self.memory = [0] * 4096

        self.load_fonts()

        self.opcode_map = {0x0000: self._0nnn_mapper,0x00E0: self._00E0,0x00EE: self._00EE,0x1000: self._1nnn,0x2000: self._2nnn,0x3000: self._3xkk,0x4000: self._4xkk,0x5000: self._5xy0,0x6000: self._6xkk,0x7000: self._7xkk,0x8000: self._8xyn_mapper,0x8001: self._8xy1,0x8002: self._8xy2,0x8003: self._8xy3,0x8004: self._8xy4,0x8005: self._8xy5,0x8006: self._8xy6,0x8007: self._8xy7,0x800E: self._8xyE,0x9000: self._9xy0,0xA000: self._Annn,0xB000: self._Bnnn,0xC000: self._Cxkk,0xD000: self._Dxyn,0xE000: self._Exnn_mapper,0xE09E: self._Ex9E,0xE0A1: self._ExA1,0xF000: self._Fxnn_mapper,0xF007: self._Fx07,0xF00A: self._Fx0A,0xF015: self._Fx15,0xF018: self._Fx18,0xF01E: self._Fx1E,0xF029: self._Fx29,0xF033: self._Fx33,0xF055: self._Fx55,0xF065: self._Fx65,}
        self.log("finished init.")

    def load_rom(self, rom_path):
        #
        """
        binary = [
            0x60, 0x09, 0x61, 0x12,
            0xA0, 0x00, 0xD0, 0x15,

            0x60, 0x00, 0x61, 0x00,
            0xA0, 0x05, 0xD0, 0x15,

            0x60, 0x09, 0x61, 0x00,
            0xA0, 0x0A, 0xD0, 0x15,

            0x60, 0x12, 0x61, 0x00,
            0xA0, 0x0F, 0xD0, 0x15,

            0x60, 0x00, 0x61, 0x06,
            0xA0, 0x14, 0xD0, 0x15,

            0x60, 0x09, 0x61, 0x06,
            0xA0, 0x19, 0xD0, 0x15,

            0x60, 0x12, 0x61, 0x06,
            0xA0, 0x1E, 0xD0, 0x15,

            0x60, 0x00, 0x61, 0x0C,
            0xA0, 0x23, 0xD0, 0x15,

            0x60, 0x09, 0x61, 0x0C,
            0xA0, 0x28, 0xD0, 0x15,

            0x60, 0x12, 0x61, 0x0C,
            0xA0, 0x2D, 0xD0, 0x15,
        ]

        for i in range(len(binary)):
            self.memory[self.memory_offset+i] = binary[i]


        return
        #"""
        self.log("loading rom...")
        with open(rom_path,"rb") as binary_file:
            binary = binary_file.read()
            for i in range(len(binary)):
                self.memory[self.memory_offset+i] = binary[i]
        self.log("finished loading rom.")
        #self.logfile.write(str([(hex(i),hex(self.memory[i])) for i in range(4096)]))

    def proccess_opcode(self):

        self.log("processing opcode"+ hex(self.opcode) +"...")

        self.vx = (self.opcode & 0x0F00) >> 8
        self.vy = (self.opcode & 0x00F0) >> 4


        op = (self.opcode & 0xF000)

        self.opcode_map.get(op,self.operation_not_found)()

        self.pc += self.increment
        self.increment = 2

        self.log("finished processing opcode"+ hex(self.opcode) +".")



    # loaded memory
    def load_fonts(self):
        self.log("loading fonts...")

        fonts = [0xF0,0x90,0x90,0x90,0xF0,0x20,0x60,0x20,0x20,0x70,0xF0,0x10,0xF0,0x80,0xF0,0xF0,0x10,0xF0,0x10,0xF0,0x90,0x90,0xF0,0x10,0x10,0xF0,0x80,0xF0,0x10,0xF0,0xF0,0x80,0xF0,0x90,0xF0,0xF0,0x10,0x20,0x40,0x40,0xF0,0x90,0xF0,0x90,0xF0,0xF0,0x90,0xF0,0x10,0xF0,0xF0,0x90,0xF0,0x90,0x90,0xE0,0x90,0xE0,0x90,0xE0,0xF0,0x80,0x80,0x80,0xF0,0xE0,0x90,0x90,0x90,0xE0,0xF0,0x80,0xF0,0x80,0xF0,0xF0,0x80,0xF0,0x80,0x80]
        for i in range(len(fonts)):
            self.memory[i] = fonts[i]
        self.log("finished loading fonts.")


    def play_sound(self):
        pass
    def decrement_timers(self):
        # decrement timers
        if self.delay_timer_register > 0:
            self.delay_timer_register -= 1
        if self.sound_timer_register > 0:
            self.sound_timer_register -= 1
        if self.sound_timer_register == 0:
            self.play_sound()


    def get_bin(self,num):
        return bin( num )[2:].zfill(8)


    def get_input(self):

        self.pressed_key = self.stdscr.getch()
        self.key_inputs = [0]*16
        if self.key_mapping.get(self.pressed_key) != None:
            self.key_inputs[self.key_mapping.get(self.pressed_key)] = 1


    def main(self, stdscr):
        curses.cbreak()
        #stdscr.nodelay(True)
        curses.halfdelay(1)
        v0=[]
        self.stdscr = stdscr
        while True:

            #if self.pc == 0x238 or self.pc ==  0x232 or (self.opcode & 0xF000 == 0xE000 or self.opcode & 0xF000 == 0xF000) and ((self.opcode & 0xFF) == 0xa1 or (self.opcode & 0xFF) == 0x9e or (self.opcode & 0xFF) == 0x0A):
            #    stdscr.nodelay(False)


            self.opcode = (self.memory[self.pc]<<8)+self.memory[self.pc+1]

            self.log("main, opcode:  " + hex(self.opcode) + " pc: "+ hex(self.pc))

            self.log(hex(self.opcode))

            #self.get_input()
            #stdscr.nodelay(True)

            self.proccess_opcode()

            stdscr.clear()
            for i in range(32):
                for j in range(64):
                    stdscr.addstr(i,j*2,"██"*self.display_buffer[i][j])

            #"""
            stdscr.addstr(1,129,"------------------")
            stdscr.addstr(1,130,"opcode:  "+hex(self.opcode))
            
            stdscr.addstr(2,129,"------------------")
            stdscr.addstr(2,130,"pc:  "+ hex(self.pc))

            stdscr.addstr(3,129,"------------------")
            stdscr.addstr(3,130,"vx:  "+hex(self.registers[self.vx]))

            stdscr.addstr(4,129,"------------------")
            stdscr.addstr(4,130,"vy:  "+hex(self.registers[self.vy]))

            stdscr.addstr(5,129,"------------------")
            stdscr.addstr(5,130,"input:  "+str(self.key_inputs))

            stdscr.addstr(6,129,"------------------")
            stdscr.addstr(6,130,"input:  "+str(self.key_mapping.get(self.pressed_key)))


            for v in range(0xf):
                stdscr.addstr(7+v,129,"------------------")
                stdscr.addstr(7+v,130,"V"+str(v)+":  "+hex(self.registers[v]))
                #stdscr.addstr(7,130,"input:  "+",".join([str((hex(i), hex(self.registers[i]))) for i in range(0xf)]))

            if hex(self.registers[0]) not in v0:
                v0.append(hex(self.registers[0]))

            stdscr.addstr(8,129,"------------------")
            #stdscr.addstr(8,130,"V0:  "+str(v0))

            stdscr.refresh()
            #stdscr.getkey()
            self.decrement_timers()

        

            self.log("end of main, opcode:  " + hex(self.opcode) + "  pc:  " + hex(self.pc))

            #time.sleep(1)



    def operation_not_found(self):
        self.log("operacion no encontrada:  " + hex(self.opcode))

        exit(hex(self.opcode)+ " " +hex(self.memory[self.pc])+" "+hex(self.pc) + "\n" +(str([hex(i) for i in self.memory])))

    def run(self, rom_path):
        self.init()
        self.load_rom(rom_path)
        #print("\t".join([str(i)+"-"+hex(self.memory[i]) for i in range(len(self.memory))]))
        self.pc = self.memory_offset
        #print(self.pc)
        curses.wrapper(self.main)

    """
    0nnn - SYS addr
    Jump to a machine code routine at nnn.

    This instruction is only used on the old computers on which Chip-8 was originally implemented. It is ignored by modern interpreters.
    """
    def _0nnn_mapper(self):
        if self.opcode == 0x0000:
            exit("exited on opcode: " + hex(self.opcode))
        op = (self.opcode & 0xF0FF)
        self.opcode_map.get(op,self.operation_not_found)()


    """
    00E0 - CLS
    Clear the display.
    """
    def _00E0(self):
        self.display_buffer = [[0 for j in range(64)] for i in range(32)]






    """
    00EE - RET
    Return from a subroutine.

    The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.
    """
    def _00EE(self):
        self.pc = self.stack.pop()
        self.increment=0



    """
    1nnn - JP addr
    Jump to location nnn.

    The interpreter sets the program counter to nnn.
    """
    def _1nnn(self):
        self.pc = self.opcode & 0x0FFF
        self.increment=0



    """
    2nnn - CALL addr
    Call subroutine at nnn.

    The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC is then set to nnn.
    """
    def _2nnn(self):
        self.stack.append(self.pc+2)
        self.pc = self.opcode & 0x0FFF
        self.increment=0


    """
    3xkk - SE Vx, byte
    Skip next instruction if Vx = kk.

    The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
    """
    def _3xkk(self):
        kk = self.opcode & 0x00FF
        if self.registers[self.vx] == kk:
            self.pc += 2


    """
    4xkk - SNE Vx, byte
    Skip next instruction if Vx != kk.

    The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
    """
    def _4xkk(self):
        kk = self.opcode & 0x00FF
        if self.registers[self.vx] != kk:
            self.pc += 2 

    """
    5xy0 - SE Vx, Vy
    Skip next instruction if Vx = Vy.

    The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
    """
    def _5xy0(self):
        if self.registers[self.vx] == self.registers[self.vy]:
            self.pc += 2 


    """
    6xkk - LD Vx, byte
    Set Vx = kk.

    The interpreter puts the value kk into register Vx.
    """
    def _6xkk(self):
        kk = self.opcode & 0x00FF
        self.registers[self.vx] = kk

    """
    7xkk - ADD Vx, byte
    Set Vx = Vx + kk.

    Adds the value kk to the value of register Vx, then stores the result in Vx.
    """
    def _7xkk(self):
        kk = self.opcode & 0x00FF
        self.registers[self.vx] = (self.registers[self.vx] + kk) & 0x00FF



    """ mapping the instructions starting with 8 """


    def _8xyn_mapper(self):
        op = (self.opcode & 0xF00F)
        if op == 0x8000:
            self._8xy0()
            return
        self.opcode_map.get(op,self.operation_not_found)()




    """
    8xy0 - LD Vx, Vy
    Set Vx = Vy.

    Stores the value of register Vy in register Vx.
    """
    def _8xy0(self):
        self.registers[self.vx] = self.registers[self.vy]

    """
    8xy1 - OR Vx, Vy
    Set Vx = Vx OR Vy.

    Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0.
    """
    def _8xy1(self):
        self.registers[self.vx] = self.registers[self.vy] | self.registers[self.vx]



    """
    8xy2 - AND Vx, Vy
    Set Vx = Vx AND Vy.

    Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND compares the corrseponding bits from two values, and if both bits are 1, then the same bit in the result is also 1. Otherwise, it is 0.
    """
    def _8xy2(self):
        self.registers[self.vx] = self.registers[self.vy] & self.registers[self.vx]


    """
    8xy3 - XOR Vx, Vy
    Set Vx = Vx XOR Vy.

    Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
    """
    def _8xy3(self):
        self.registers[self.vx] = self.registers[self.vy] ^ self.registers[self.vx]



    """
    8xy4 - ADD Vx, Vy
    Set Vx = Vx + Vy, set VF = carry.

    The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
    """
    def _8xy4(self):
        val = (self.registers[self.vy] & 0xFF) + (self.registers[self.vx] & 0xFF)
        self.registers[0xf] = (val & 0xF00) >> 8
        self.registers[self.vx] = (val) & 0xFF



    """
    8xy5 - SUB Vx, Vy
    Set Vx = Vx - Vy, set VF = NOT borrow.

    If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
    """
    def _8xy5(self):
        self.registers[self.vx] = (self.registers[self.vx] - self.registers[self.vy]) & 0xFF
        self.registers[0xf] = int(self.registers[self.vx] >= self.registers[self.vy])

    """
    8xy6 - SHR Vx {, Vy}
    Set Vx = Vx SHR 1.

    If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
    """
    def _8xy6(self):
        self.registers[0xf] = self.registers[self.vx] & 0x1
        self.registers[self.vx] = int(self.registers[self.vx] / 2)



    """
    8xy7 - SUBN Vx, Vy
    Set Vx = Vy - Vx, set VF = NOT borrow.

    If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
    """
    def _8xy7(self):
        self.registers[self.vx] = (self.registers[self.vy] - self.registers[self.vx]) & 0xFF
        self.registers[0xf] = int(self.registers[self.vy] > self.registers[self.vx])



    """
    8xyE - SHL Vx {, Vy}
    Set Vx = Vx SHL 1.

    If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
    """
    def _8xyE(self):
        self.registers[0xf] = (self.registers[self.vx] & 0x80) >> 7
        self.registers[self.vx] = (self.registers[self.vx] * 2) & 0xFF



    """
    9xy0 - SNE Vx, Vy
    Skip next instruction if Vx != Vy.

    The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
    """
    def _9xy0(self):
        if self.registers[self.vx] != self.registers[self.vy]:
            self.pc += 2

    """
    Annn - LD I, addr
    Set I = nnn.

    The value of register I is set to nnn.
    """
    def _Annn(self):
        self.index_register = self.opcode & 0x0FFF


    """
    Bnnn - JP V0, addr
    Jump to location nnn + V0.

    The program counter is set to nnn plus the value of V0.
    """
    def _Bnnn(self):
        self.pc = (self.opcode & 0x0FFF) + self.registers[0]
        self.increment=0



    """
    Cxkk - RND Vx, byte
    Set Vx = random byte AND kk.

    The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.
    """
    def _Cxkk(self):
        r = random.randint(0,255)
        kk = self.opcode & 0x00FF
        self.registers[self.vx] = r & kk


    """
    Dxyn - DRW Vx, Vy, nibble
    Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

    The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen. See instruction 8xy3 for more information on XOR, and section 2.4, Display, for more information on the Chip-8 screen and sprites.
    """
    def _Dxyn(self):
        n = self.opcode & 0x000F
        read_mem_bytes = self.memory[self.index_register:self.index_register+n+1]
        self.registers[0xf] = 0

        for i in range(n):
            y = self.registers[self.vy]
            y = y + i if y + i < 32 else (y + i)%32

            writing_byte = self.get_bin(read_mem_bytes[i])

            for j in range(8):
                x = self.registers[self.vx]
                x = x + j if x + j < 64 else (x + j)%64

                self.display_buffer[y][x] ^= int(writing_byte[j])

                if self.display_buffer[y][x] == 0 and int(writing_byte[j]) == 1:
                    self.registers[0xf] = 1

                #self.display_buffer[i][j] = int(writing_byte[j]) ^ self.display_buffer[i][j]


    """ mapper for Ennn instructions """
    def _Exnn_mapper(self):
        self._0nnn_mapper()


    """
    Ex9E - SKP Vx
    Skip next instruction if key with the value of Vx is pressed.

    Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.
    """
    def _Ex9E(self):
        self.get_input()

        if self.key_mapping.get(self.pressed_key)  == (self.registers[self.vx] & 0xF):
            self.pc += 2


    """
    ExA1 - SKNP Vx
    Skip next instruction if key with the value of Vx is not pressed.

    Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.
    """
    def _ExA1(self):
        self.get_input()

        if self.key_mapping.get(self.pressed_key) != (self.registers[self.vx] & 0xF):
            self.pc += 2


    """ mapper for Fnnn instructions """
    def _Fxnn_mapper(self):
        self._0nnn_mapper()


    """
    Fx07 - LD Vx, DT
    Set Vx = delay timer value.

    The value of DT is placed into Vx.
    """
    def _Fx07(self):
        self.registers[self.vx] = self.delay_timer_register & 0xFF

    """
    Fx0A - LD Vx, K
    Wait for a key press, store the value of the key in Vx.

    All execution stops until a key is pressed, then the value of that key is stored in Vx.
    """
    def _Fx0A(self):
        if self.key_mapping.get(self.pressed_key) == None:
            nocbreak()
            stdscr.nodelay(False)
            self.get_input()

        self.registers[self.vx] = self.key_mapping.get(self.pressed_key)
        stdscr.nodelay(True)
        stdscr.halfdelay(1)

    """
    Fx15 - LD DT, Vx
    Set delay timer = Vx.

    DT is set equal to the value of Vx.
    """
    def _Fx15(self):
        self.delay_timer_register = self.registers[self.vx] & 0xFF

    """
    Fx18 - LD ST, Vx
    Set sound timer = Vx.

    ST is set equal to the value of Vx.
    """
    def _Fx18(self):
        self.sound_timer_register = self.registers[self.vx] & 0xFF


    """
    Fx1E - ADD I, Vx
    Set I = I + Vx.

    The values of I and Vx are added, and the results are stored in I.
    """
    def _Fx1E(self):
        self.index_register = (self.index_register + self.registers[self.vx]) & 0xFFFF


    """
    Fx29 - LD F, Vx
    Set I = location of sprite for digit Vx.

    The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
    """
    def _Fx29(self):
        self.index_register = (self.registers[(self.vx & 0xF)]*5) & 0xFFF


    """
    Fx33 - LD B, Vx
    Store BCD representation of Vx in memory locations I, I+1, and I+2.

    The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.
    """
    def _Fx33(self):
        s = "00" + str(self.registers[self.vx])
        self.memory[self.index_register+2] = int(s[-1]) & 0xF
        self.memory[self.index_register+1] = int(s[-2]) & 0xF
        self.memory[self.index_register] = int(s[-3]) & 0xF

    """
    Fx55 - LD [I], Vx
    Store registers V0 through Vx in memory starting at location I.

    The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
    """
    def _Fx55(self):

        for i in range(self.vx+1):
            self.memory[self.get_mem_addr(self.index_register,i)] = self.registers[i] & 0xFF


    """
    Fx65 - LD Vx, [I]
    Read registers V0 through Vx from memory starting at location I.

    The interpreter reads values from memory starting at location I into registers V0 through Vx.
    """
    def _Fx65(self):
        for i in range(self.vx+1):
            self.registers[i] = self.memory[self.get_mem_addr(self.index_register,i)] & 0xFF


    def get_mem_addr(self, f, t):
            result = f+t
            if result >= 4096:
                result = result%4096
            return result

def start():


    rom = __file__.replace("chip8.py","tetris.ch8")
    #rom = __file__.replace("chip8.py","pong.ch8")

    c = Chip8()
    c.run(rom)

if __name__ == "__main__":
    start()
