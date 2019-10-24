from opcode import opmap, opname

def generate_instr(filename: str):
    with open(filename, "w", encoding="utf8") as file:
        for name, code in opmap.items():
            file.write(f"{name} = {code}\n")
        file.write("opmap = {\n")
        for code, name in enumerate(opname):
            file.write(f"\t{code}: {name!r}, \n")
        file.write("}\n")

"""
def generate_stacksize(filename: str):
    with open(filename, "w", encoding="utf8") as file:
        file.write("from instruction.instruction import Instruction\n")
        file.write("from instruction import code\n")
        file.write("def stacksize(instr: Instruction) -> int:\n")
        for name, code in opmap.items():
            file.write(f"\tif instr.op == code.{name}: \n")
            file.write(f"\t\tpass\n")
        file.write("\n")
"""

if __name__ == "__main__":
    generate_instr("code.py")
    # generate_stacksize('stacksize.py')