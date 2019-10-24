from types import FunctionType as funcType
from types import CodeType as codeType
from opcode import opmap, opname
# from uuid import uuid4 as label_id

NoneType = type(None)

def to_bin(x: int, n: int = 16) -> str:
    """
    x: int
    n: int ; bit wide
    """
    return format(x, 'b').zfill(n)
def to_int(b: str) -> int:
    """
    b: str ; binary string
    """
    return int(b, 2)

class CopyCode(dict):
    def __init__(self, co: codeType):
        dict.__init__(self)
        """
        'co_argcount', 'co_cellvars',
        'co_code', 'co_consts',
        'co_filename', 'co_firstlineno',
        'co_flags', 'co_freevars',
        'co_kwonlyargcount', 'co_lnotab',
        'co_name', 'co_names', 'co_nlocals',
        'co_stacksize', 'co_varnames'
        code(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
        constants, names, varnames, filename, name, firstlineno,
        lnotab[, freevars[, cellvars]])
        """
        self["argcount"]       = co.co_argcount                                   # int
        self["cellvars"]       = list(co.co_cellvars)                             # [Cell]           => tuple
        self["codestring"]     = list(co.co_code)                                 # [int]            => bytes
        self["constants"]      = [(type(const), const) for const in co.co_consts] # [(type, object)] => tuple
        self["filename"]       = co.co_filename                                   # str
        self["firstlineno"]    = co.co_firstlineno                                # int
        self["flags"]          = co.co_flags                                      # int
        self["freevars"]       = list(co.co_freevars)                             # [Obj]            => tuple
        self["kwonlyargcount"] = co.co_kwonlyargcount                             # int
        self["lnotab"]         = co.co_lnotab                                     # bytes
        self["name"]           = co.co_name                                       # str
        self["names"]          = list(co.co_names)                                # [str]            => tuple
        self["nlocals"]        = co.co_nlocals                                    # int
        self["stacksize"]      = co.co_stacksize                                  # int
        self["varnames"]       = list(co.co_varnames)                             # [str]            => tuple

    def _build(self,
               argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
               constants, names, varnames, filename, name,
               firstlineno, lnotab,
               freevars, cellvars ):
        return codeType(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
                        constants, names, varnames, filename, name,
                        firstlineno, lnotab,
                        freevars, cellvars)

    def build(self):
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

class CopyFunc(dict):
    def __init__(self, f: funcType, clear: bool = False):
        dict.__init__(self)
        self["__annotations__"] = f.__annotations__
        self["__doc__"] = f.__doc__
        self["__defaults__"] = f.__defaults__
        self["__dict__"] = f.__dict__
        self["__globals__"] = dict(f.__globals__) if clear else f.__globals__
        self["__kwdefaults__"] = f.__kwdefaults__
        self["__code__"] = CopyCode(f.__code__)
        self["__name__"] = f.__name__
        self["__closure__"] = f.__closure__

    def build(self):
        new_func = funcType(self["__code__"].build(), self["__globals__"],
                         self["__name__"], self["__defaults__"],
                         self["__closure__"])
        new_func.__annotations__ = self["__annotations__"]
        new_func.__dict__ = self["__dict__"]
        new_func.__kwdefaults__ = self["__kwdefaults__"]
        new_func.__doc__ = self["__doc__"]
        return new_func

    def obj_build_cell(self, val: object) -> object:
        def _():
            return val
        return _.__closure__[0]

    def build_global(self, name: str) -> int:
        if name not in self["__code__"]["names"]:
            self["__code__"]["names"].append(name)
        return self["__code__"]["names"].index(name)

    def build_local(self, name: str) -> int:
        if name not in self["__code__"]["varnames"]:
            self["__code__"]["varnames"].append(name)
        return self["__code__"]["varnames"].index(name)

    def build_cell(self, name: str) -> int:
        if name not in self["__code__"]["cellvars"]:
            self["__code__"]["cellvars"].append(name)
        return self["__code__"]["cellvars"].index(name)

    def build_free(self, name: str) -> int:
        if name not in self["__code__"]["freevars"]:
            self["__code__"]["freevars"].append(name)
        return self["__code__"]["freevars"].index(name)

    def build_constant(self, obj: object) -> int:
        const = (type(obj), obj) # True: Bool and 1: Int
        if const not in self["__code__"]["constants"]:
            self["__code__"]["constants"].append(const)
        return self["__code__"]["constants"].index(const)

    def get_global_name(self, idx: int) -> str:
        return self["__code__"]["names"][idx]

    def get_local_name(self, idx: int) -> str:
        return self["__code__"]["varnames"][idx]

    def get_cell_name(self, idx: int) -> str:
        return self["__code__"]["cellvars"][idx]

    def get_free_name(self, idx: int) -> str:
        return self["__code__"]["freevars"][idx]

    def get_constant(self, idx: int) -> object:
        _, val = self["__code__"]["constants"][idx]
        return val

    def set_global(self, name: str, value: object):
        self.build_global(name)
        self["__globals__"][name] = value

    def set_local(self, name: str, value: object):
        # idx = self.build_local(name)
        # self["__code__"]["codestring"] = [opmap["STORE_FAST"], idx] + self["__code__"]["codestring"]
        raise NotImplementedError

def make_function(name, code: codeType, closure, globals, defaults, kwdefaults, doc, annotations):
    raise NotImplementedError

def make_code(...):
    raise NotImplementedError

def calculus_stacksize(code: codeType):
    raise NotImplementedError
