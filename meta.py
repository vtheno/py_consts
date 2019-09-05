from types import FunctionType as funcType
from types import CodeType as codeType
from opcode import opmap, opname

NoneType = type(None)

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
        self["argcount"]       = co.co_argcount       # int
        self["cellvars"]       = list(co.co_cellvars) # [Cell]    => tuple
        self["codestring"]     = list(co.co_code)     # [int]     => bytes
        self["constants"]      = list(co.co_consts)   # [object]  => tuple
        self["filename"]       = co.co_filename       # str
        self["firstlineno"]    = co.co_firstlineno    # int
        self["flags"]          = co.co_flags          # int
        self["freevars"]       = list(co.co_freevars) # [Obj]     => tuple
        self["kwonlyargcount"] = co.co_kwonlyargcount # int
        self["lnotab"]         = co.co_lnotab         # bytes
        self["name"]           = co.co_name           # str
        self["names"]          = list(co.co_names)    # [str]     => tuple
        self["nlocals"]        = co.co_nlocals        # int
        self["stacksize"]      = co.co_stacksize      # int
        self["varnames"]       = list(co.co_varnames) # [str]     => tuple

    def _build(self,
               argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
               constants, names, varnames, filename, name,
               firstlineno, lnotab,
               freevars, cellvars ):
        return codeType(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
                        constants, names, varnames, filename, name,
                        firstlineno, lnotab,
                        freevars, cellvars)
    def __repr__(self):
        return "\n".join("{} {} {}".format(i, 
                                           opname[self["codestring"][i]],
                                           self["codestring"][i + 1]) for i in range(0, len(self["codestring"]), 2))

    def build(self):
        self["cellvars"]   = tuple(self["cellvars"])
        self["codestring"] = bytes(self["codestring"])
        self["constants"]  = tuple(self["constants"])
        self["freevars"]   = tuple(self["freevars"])
        self["names"]      = tuple(self["names"])
        self["varnames"]   = tuple(self["varnames"])
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
        if obj not in self["__code__"]["constants"]:
            self["__code__"]["constants"].append(obj)
        return self["__code__"]["constants"].index(obj)


    def get_global_name(self, idx: int) -> str:
        return self["__code__"]["names"][idx]

    def get_local_name(self, idx: int) -> str:
        return self["__code__"]["varnames"][idx]

    def get_cell_name(self, idx: int) -> str:
        return self["__code__"]["cellvars"][idx]

    def get_free_name(self, idx: int) -> str:
        return self["__code__"]["freevars"][idx]

    def get_constant(self, idx: int) -> object:
        return self["__code__"]["constants"][idx]



    def set_global(self, name: str, value: object):
        self.build_global(name)
        self["__globals__"][name] = value

    def set_local(self, name: str, value: object):
        # idx = self.build_local(name)
        # self["__code__"]["codestring"] = [opmap["STORE_FAST"], idx] + self["__code__"]["codestring"]
        raise NotImplementedError

def find_all_store_global_const(fo: CopyFunc) -> dict:
    # co: CopyCode, code: [int] 
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    env = {}
    for i in range(0, length, 2):
        if i + 3 <= length:
            op, arg = code[i], code[i + 1]
            nextop, nextarg = code[i + 2], code[i + 3]
            if op == opmap["LOAD_CONST"] and nextop == opmap["STORE_GLOBAL"]:
                env[fo.get_global_name(nextarg)] = fo.get_constant(arg)
    return env


def patch_global_const_to_const(fo: CopyFunc) -> None:
    # co: CopyCode, code: [int] 
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    changed = True
    while changed:
        changed = False    
        env = find_all_store_global_const(fo)
        for i in range(0, length, 2):
            op, arg = code[i], code[i + 1]
            if op == opmap["LOAD_GLOBAL"]:
                name = fo.get_global_name(arg)
                if name in env.keys():
                    const_val = env[name] 
                    if isinstance(const_val, (bool, NoneType, int, float, str, tuple)):
                        changed = True    
                        const_idx = fo.build_constant( const_val )
                        code[i], code[i + 1] =  opmap["LOAD_CONST"], const_idx
        
        patch_const_build_tuple_to_const(fo)
        patch_const_binary_to_const(fo)

def find_all_store_local_const(fo: CopyFunc) -> dict:
    # co: CopyCode, code: [int] 
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    env = {}
    for i in range(0, length, 2):
        if i + 3 <= length:
            op, arg = code[i], code[i + 1]
            nextop, nextarg = code[i + 2], code[i + 3]
            if op == opmap["LOAD_CONST"] and nextop == opmap["STORE_FAST"]:
                env[fo.get_local_name(nextarg)] = fo.get_constant(arg)
    return env

def patch_local_const_to_const(fo: CopyFunc) -> None:
    # co: CopyCode, code: [int] 
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    
    changed = True
    while changed:
        changed = False    
        env = find_all_store_local_const(fo)
        # print("-"*100)
        # print(co)
        # print("-"*100)
        for i in range(0, length, 2):
            op, arg = code[i], code[i + 1]
            if op == opmap["LOAD_FAST"]:
                name = fo.get_local_name(arg)
                # print(name, env)
                if name in env.keys():
                    const_val = env[name] 
                    if isinstance(const_val, (bool, NoneType, int, float, str, tuple)):
                        changed = True
                        const_idx = fo.build_constant( const_val )
                        code[i], code[i + 1] = opmap["LOAD_CONST"], const_idx
        
        patch_const_build_tuple_to_const(fo)
        patch_const_binary_to_const(fo)

def patch_const_store_to_nop(fo: CopyCode) -> None:
    # co: CopyCode, code: [int] 
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    env = find_all_store_global_const(fo)
    env.update(find_all_store_local_const(fo))
    for i in range(0, length, 2):
        if i + 3 <= length:
            op, arg = code[i], code[i + 1]
            nextop, nextarg = code[i + 2], code[i + 3]
            if op == opmap["LOAD_CONST"] and nextop in [opmap["STORE_GLOBAL"], opmap["STORE_FAST"]]:
                name = fo.get_local_name(nextarg) if nextop == opmap["STORE_FAST"] else fo.get_global_name(nextarg)
                if name in env.keys():
                    code[i], code[i + 1] = opmap["NOP"], 0
                    code[i + 2], code[i + 3] = opmap["NOP"], 0

def patch_const_build_tuple_to_const(fo: CopyFunc) -> None:
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    changed = True
    while changed:
        changed = False    
        for i in range(0, length, 2):
            if i + 3 <= length:
                op, arg = code[i], code[i + 1]
                if op == opmap["BUILD_TUPLE"]:
                    before = []
                    push = before.append
                    flag = True
                    for count in range(1, arg + 1):
                        offset = i - 2 * count
                        cur = code[offset]
                        push( (cur, code[offset + 1]) )
                        flag = flag and cur == opmap["LOAD_CONST"]
                    if flag:
                        changed = True    
                        for count in range(1, arg + 1):
                            offset = i - 2 * count
                            code[offset], code[offset + 1] = opmap["NOP"], 0
                        const = tuple(reversed([fo.get_constant(arg) for _, arg in before]))
                        const_idx = fo.build_constant( const )
                        code[i], code[i + 1] = opmap["LOAD_CONST"], const_idx

def patch_const_binary_to_const(fo: CopyFunc) -> None:
    # co: CopyCode, code: [int] 
    co = fo["__code__"]
    code = co["codestring"]
    import operator
    env = {
        opmap["BINARY_POWER"]: operator.pow,
        opmap["BINARY_MULTIPLY"]: operator.mul,
        opmap["BINARY_MATRIX_MULTIPLY"]: operator.matmul,
        opmap["BINARY_FLOOR_DIVIDE"]: operator.floordiv,
        opmap["BINARY_TRUE_DIVIDE"]: operator.truediv,
        opmap["BINARY_MODULO"]: operator.mod,
        opmap["BINARY_ADD"]: operator.add,
        opmap["BINARY_SUBTRACT"]: operator.sub,
        opmap["BINARY_SUBSCR"]: operator.getitem, # tuple support
        opmap["BINARY_LSHIFT"]: operator.lshift,
        opmap["BINARY_RSHIFT"]: operator.rshift,
        opmap["BINARY_AND"]:  operator.and_,
        opmap["BINARY_XOR"]: operator.xor,
        opmap["BINARY_OR"]: operator.or_,
    }
    length = len(code)
    changed = True
    while changed:
        changed = False
        for i in range(0, length, 2):
            if i + 5 <= length:
                op, arg = code[i], code[i + 1]
                nextop, nextarg = code[i + 2], code[i + 3]
                lastop, lastarg = code[i + 4], code[i + 5]
                if op == nextop == opmap["LOAD_CONST"] and lastop in env.keys():
                    changed = True
                    val = env[lastop](fo.get_constant(arg), fo.get_constant(nextarg))
                    const_idx = fo.build_constant(val)
                    code[i], code[i + 1] = opmap["NOP"], 0
                    code[i + 2], code[i + 3] = opmap["NOP"], 0
                    code[i + 4], code[i + 5] = opmap["LOAD_CONST"], const_idx

def simple_patch_drop_nop(fo: CopyFunc) -> None:
    # co: CopyCode, code: [int]  
    # todo support if statement , loop statement, etc...
    co = fo["__code__"]
    code = co["codestring"]
    def g():
        length = len(code)    
        for i in range(0, length, 2):
            op, arg = code[i], code[i + 1]
            if op != opmap["NOP"]:
                yield op
                yield arg
    co["codestring"] = list(g())