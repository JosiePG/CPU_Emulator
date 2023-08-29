import tkinter as tk
class CPU6502:
    def __init__(self):
        # CPU registers
        self.A = 0  # Accumulator
        self.X = 0  # X register
        self.Y = 0  # Y register
        self.PC = 0x8000  # Program counter (start address)
        self.SP = 0x01FF  # Stack pointer (initialized to top of stack)
        self.SR = 0x20  # Status register (initialized with the 'I' flag set)

        # Memory
        self.memory = [0] * 65536  # 64KB of memory

    def load_program(self, program):
        # Load program into memory starting at address 0x8000
        for addr, value in enumerate(program, start=0x8000):
            self.memory[addr] = value
        print("here")

    def fetch(self):
        # Fetch the instruction at the current PC address
        opcode = self.memory[self.PC]
        return opcode

    def execute(self, opcode):
        if opcode == 0x00:  # BRK instruction
            # Implement the BRK instruction logic
            # Push the PC and status register onto the stack
            pc_high_byte = (self.PC >> 8) & 0xFF
            pc_low_byte = self.PC & 0xFF
            status = self.SR | 0x30  # Set the B and I flags

            # Push the high byte of the PC onto the stack
            self.memory[self.SP] = pc_high_byte
            self.SP -= 1

            # Push the low byte of the PC onto the stack
            self.memory[self.SP] = pc_low_byte
            self.SP -= 1

            # Push the status register onto the stack
            self.memory[self.SP] = status
            self.SP -= 1

            # Set the interrupt disable flag
            self.SR |= 0x04

            # Set the PC to the address stored in the interrupt vector
            self.PC = (self.memory[0xFFFF] << 8) | self.memory[0xFFFE]
        else:
            # Opcode execution logic for other instructions
            if opcode == 0xA9:  # LDA Immediate
                self.PC += 1  # Increment PC to get the operand
                operand = self.memory[self.PC]
                self.A = operand
                # Update status flags (e.g., zero and negative flags)
                self.update_flags_zero_negative(self.A)
            elif opcode == 0xA2:  # LDX Immediate
                self.PC += 1  # Increment PC to get the operand
                operand = self.memory[self.PC]
                self.X = operand
                # Update status flags (e.g., zero and negative flags)
                self.update_flags_zero_negative(self.X)
            elif opcode == 0xA0:  # LDY Immediate
                self.PC += 1  # Increment PC to get the operand
                operand = self.memory[self.PC]
                self.Y = operand
                # Update status flags (e.g., zero and negative flags)
                self.update_flags_zero_negative(self.Y)
            elif opcode == 0x85:  # STA Absolute Zero Page
                address = self.memory[self.PC + 1]
                self.memory[address] = self.A
            elif opcode == 0x86:  # STX Absolute Zero Page
                address = self.memory[self.PC + 1]
                self.memory[address] = self.X
            elif opcode == 0x84:  # STY Absolute Zero Page
                address = self.memory[self.PC + 1]
                self.memory[address] = self.Y
            elif opcode == 0xA5:  # LDA Absolute Zero Page
                address = self.memory[self.PC + 1]
                self.A = self.memory[address]
                self.update_flags_zero_negative(self.A)
            elif opcode == 0xA6:  # LDX Absolute Zero Page
                address = self.memory[self.PC + 1]
                self.X = self.memory[address]
                self.update_flags_zero_negative(self.X)
            elif opcode == 0xA4:  # LDY Absolute Zero Page
                address = self.memory[self.PC + 1]
                self.Y = self.memory[address]
                self.update_flags_zero_negative(self.Y)
            elif opcode == 0x69:  # ADC Immediate
                self.PC += 1  # Increment PC to get the operand
                operand = self.memory[self.PC]
                result = self.A + operand
                self.A = result & 0xFF
                # Update carry and overflow flags (not shown in the code)
                # Update zero and negative flags
                self.update_flags_zero_negative(self.A)
            elif opcode == 0xE8:  # INX
                self.X = (self.X + 1) & 0xFF
                self.update_flags_zero_negative(self.X)
            elif opcode == 0xC8:  # INY
                self.Y = (self.Y + 1) & 0xFF
                self.update_flags_zero_negative(self.Y)
            elif opcode == 0x8D:  # STA Absolute
                address = self.memory[self.PC + 1] | (self.memory[self.PC + 2] << 8)
                self.memory[address] = self.A
        self.PC += 1

    # Add more instructions here as needed

    def update_flags_zero_negative(self, value):
        # Set or clear zero flag based on whether value is zero
        if value == 0:
            self.SR |= 0x02  # Set zero flag (bit 1)
        else:
            self.SR &= ~0x02  # Clear zero flag (bit 1)

        # Set or clear negative flag based on the sign of value
        if value & 0x80:
            self.SR |= 0x80  # Set negative flag (bit 7)
        else:
            self.SR &= ~0x80  # Clear negative flag (bit 7)


    def run(self):
        while self.PC < len(self.memory):  # Continue until the end of the program
            opcode = self.fetch()
            if opcode == 0x00:  # BRK instruction
                break  # Terminate the program
            self.execute(opcode)

class CPUEmulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Emulator")

        self.cpu = CPU6502()
        self.root.configure(bg="black")

        # Instruction Entry
        self.instruction_label = tk.Label(root, text="Opcode:")
        self.instruction_label.pack()
        self.instruction_entry = tk.Entry(root)
        self.instruction_entry.pack()

        # Operand Entry
        self.operand_label = tk.Label(root, text="Operand:")
        self.operand_label.pack()
        self.operand_entry = tk.Entry(root)
        self.operand_entry.pack()

        # Execute Button
        self.execute_button = tk.Button(root, text="Execute", command=self.execute_instruction)
        self.execute_button.pack()

        # Output Text
        self.output_text = tk.Text(root, height=10, width=40)
        self.output_text.pack()

        # Instruction Information
        instruction_info = """
        Possible Instructions:
        LDA (Load Accumulator) - Opcode: A9, Operand: 00FF (hex)
        LDX (Load X Register) - Opcode: A2, Operand: 00FF (hex)
        LDY (Load Y Register) - Opcode: A0, Operand: 00FF (hex)
        STA (Store Accumulator) - Opcode: 85, Operand: 00FF (hex)
        STX (Store X Register) - Opcode: 86, Operand: 00FF (hex)
        STY (Store Y Register) - Opcode: 84, Operand: 00FF (hex)
        ADC (Add with Carry) - Opcode: 69, Operand: 00FF (hex)
        INX (Increment X Register) - Opcode: E8, Operand: (any number for placeholder)
        INY (Increment Y Register) - Opcode: C8, Operand: (any number for placeholder)
        """
        self.instruction_info_label = tk.Label(root, text=instruction_info, justify=tk.LEFT,font=("Arial", 12))
        self.instruction_info_label.pack()

    def execute_instruction(self):
        instruction = self.instruction_entry.get()
        operand = self.operand_entry.get()

        # Convert instruction and operand to bytes or integers as needed
        try:
            instruction = int(instruction, 16)  # Convert hexadecimal string to integer
            operand = int(operand, 16)  # Convert hexadecimal string to integer
        except ValueError:
            # Handle invalid input
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Invalid input. Please enter valid hexadecimal values.\n")
            return

        # Ensure instruction and operand are in the range 0-255 (1 byte)
        if instruction < 0 or instruction > 255 or operand < 0 or operand > 255:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Instruction and operand must be in the range 0-255.\n")
            return

        # Load the program into the CPU
        program = [instruction, operand]
        self.cpu.load_program(program)
 

        # Capture the standard output to display CPU state
        import sys
        original_stdout = sys.stdout
        sys.stdout = self.TextRedirector(self.output_text)

        # Run the CPU program
        self.cpu.PC = 0x8000  # Reset the program counter to the start address
        self.cpu.run()

        # Print the final CPU state and memory content
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Final CPU State:\n")
        self.output_text.insert(tk.END, f"A: {self.cpu.A}\n")
        self.output_text.insert(tk.END, f"X: {self.cpu.X}\n")
        self.output_text.insert(tk.END, f"Y: {self.cpu.Y}\n")
        self.output_text.insert(tk.END, f"Memory at $10: {self.cpu.memory[0x0010]:02X}\n")  # Corrected memory address
        self.output_text.insert(tk.END, f"Memory at $11: {self.cpu.memory[0x0011]:02X}\n")  # Corrected memory address
        self.output_text.insert(tk.END, f"Memory at $12: {self.cpu.memory[0x0012]:02X}\n")  # Corrected memory address
        self.output_text.insert(tk.END, f"Memory at $0200: {self.cpu.memory[0x0200]:02X}\n")  # Corrected memory address


        # Restore the standard output
        sys.stdout = original_stdout
    class TextRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUEmulatorGUI(root)
    root.mainloop()

        



