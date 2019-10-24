from types import CodeType, CellType, FunctionType
from bintool import to_bin, to_int
from instruction.instruction import Instruction
from instruction.instruction import Label, label
from instruction.instruction import codelist
from instruction import code


class Code(dict):
    def __init__(self):
        dict.__init__(self)
        self["argcount"]        = 0                                                # int
        self["posonlyargcount"] = 0                                                # int
        self["kwonlyargcount"]  = 0                                                # int
        self["cellvars"]        = []                                               # [Cell] => tuple
        self["codestring"]      = []                                               # [int] => bytes
        self["constants"]       = []                                               # [(type, id, object)] => tuple
        self["filename"]        = "<Code filename>"                                # str
        self["firstlineno"]     = 1                                                # int
        self["flags"]           = 0                                                # int
        self["freevars"]        = []                                               # [Obj]  => tuple
        self["lnotab"]          = b''                                              # bytes
        self["name"]            = "<Code name>"                                    # str
        self["names"]           = []                                               # [str] => tuple
        self["nlocals"]         = 0                                                # int
        self["stacksize"]       = 0                                                # int
        self["varnames"]        = []                                               # [str] => tuple
    
    def _build(self,
               argcount, posonlyargcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
               constants, names, varnames, filename, name,
               firstlineno, lnotab,
               freevars, cellvars ):
        return codeType(argcount, posonlyargcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
                        constants, names, varnames, filename, name,
                        firstlineno, lnotab,
                        freevars, cellvars)

    def build(self):
        self.prebuild()
        self["cellvars"]   = tuple(self["cellvars"])
        self["codestring"] = bytes(self["codestring"])
        self["constants"]  = tuple([const for _, const in self["constants"]])
        self["freevars"]   = tuple(self["freevars"])
        self["names"]      = tuple(self["names"])
        self["varnames"]   = tuple(self["varnames"])
        self["nlocals"]    = len(self["varnames"]) + self["argcount"]
        # if not self["varnames"]:
        #     # co_flags NEWLOCALS == 0x10
        #     bstring_list = list(to_bin(self["flags"]))
        #     bstring_list[-2] = '0'
        #     self["flags"] = to_int(''.join(bstring_list))
        bstring_list = list(to_bin(self["flags"]))
        bstring_list[-2] = '1' # always add a NEWLOCALS flag
        self["flags"] = to_int(''.join(bstring_list))
        return self._build(**self)

    def prebuild(self):
        # calc flags, stacksize, nlocals, argcount, posonlyargcount, kwonlyargcount ...
        raise NotImplementedError
    def calculus_stacksize(self):
        raise NotImplementedError

labels, consts, names, codestring = codelist([
    Instruction(code.LOAD_NAME, "range"),               # 0
    Instruction(code.LOAD_CONST, 10),                   # 2
    Instruction(code.CALL_FUNCTION, 1),                 # 4
    Instruction(code.GET_ITER),                         # 6
    (label[1], Instruction(code.FOR_ITER, label[2])),   # 8
    Instruction(code.STORE_NAME, "i"),                  # 10
    Instruction(code.LOAD_NAME, "print"),               # 12
    Instruction(code.LOAD_NAME, "i"),                   # 14
    Instruction(code.CALL_FUNCTION, 1), # argc = 1      # 16
    Instruction(code.POP_TOP),                          # 18
    Instruction(code.JUMP_ABSOLUTE, label[1]),          # 20
    (label[2], Instruction(code.LOAD_CONST, None)),     # 22
    Instruction(code.LOAD_NAME, "print"),               # 24
    Instruction(code.LOAD_CONST, 10),                   # 26
    Instruction(code.CALL_FUNCTION, 1),                 # 28
    Instruction(code.RETURN_VALUE),                     # 30
])
print(labels)
print(consts)
print(names)
for instr in codestring:
    print("\t", instr, instr.pack())
