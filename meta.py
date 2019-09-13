from types import FunctionType as funcType
from types import CodeType as codeType
from opcode import opmap, opname, cmp_op
from uuid import uuid4 as label_id
import operator
import inspect

NoneType = type(None)
constant_types = (bool, NoneType, int, float, str, tuple)

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

def constants_base(fo):
    patch_const_build_tuple_to_const(fo)
    patch_const_binary_to_const(fo)
    patch_const_compare_to_const(fo)

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
            if op == opmap["LOAD_CONST"] and nextop == opmap["STORE_GLOBAL"] and count_of_store(code, nextop, nextarg) == 1:
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
                    if isinstance(const_val, constant_types):
                        changed = True
                        const_idx = fo.build_constant( const_val )
                        code[i], code[i + 1] =  opmap["LOAD_CONST"], const_idx
        constants_base(fo)

def count_of_store(code: [int], target_op: int, target_arg: int) -> int:
    length = len(code)
    count = 0
    for i in range(0, length, 2):
        op, arg = code[i], code[i + 1]
        if op == target_op and arg == target_arg:
            count += 1
    return count

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
            if op == opmap["LOAD_CONST"] and nextop == opmap["STORE_FAST"] and count_of_store(code, nextop, nextarg) == 1:
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
                if name in env.keys():
                    const_val = env[name]
                    if isinstance(const_val, constant_types):
                        changed = True
                        const_idx = fo.build_constant( const_val )
                        # print(name, env, const_val, const_idx)
                        code[i], code[i + 1] = opmap["LOAD_CONST"], const_idx
        constants_base(fo)


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

def patch_const_build_tuple_to_const(fo: CopyFunc) -> bool:
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    changed = True
    result = False
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
                        cur, cur_arg = code[offset], code[offset + 1]
                        push( (cur, cur_arg) )
                        flag = flag and cur == opmap["LOAD_CONST"]
                    if flag:
                        changed = True
                        result = True
                        for count in range(1, arg + 1):
                            offset = i - 2 * count
                            code[offset], code[offset + 1] = opmap["NOP"], 0
                        const = tuple(reversed([fo.get_constant(arg) for _, arg in before]))
                        const_idx = fo.build_constant( const )
                        code[i], code[i + 1] = opmap["LOAD_CONST"], const_idx
    return result

def patch_const_compare_to_const(fo: CopyFunc) -> bool:
    # co: CopyCode, code: [int]
    co = fo["__code__"]
    code = co["codestring"]
    co = fo["__code__"]
    def in_(a, b):
        print("IN", a, b)
        return a in b
    def not_in(a, b):
        return a not in b
    env = {
        '<'     :  operator.lt,
        '<='    : operator.le,
        '=='    : operator.eq,
        '!='    : operator.ne,
        '>'     : operator.gt,
        '>='    : operator.ge,
        'is'    : operator.is_,
        'is not': operator.is_not,
        'in'    : in_,
        'not in': not_in,
    }
    length = len(code)
    changed = True
    result = False
    while changed:
        changed = False
        for i in range(0, length, 2):
            if i + 5 <= length:
                op, arg = code[i], code[i + 1]
                nextop, nextarg = code[i + 2], code[i + 3]
                lastop, lastarg = code[i + 4], code[i + 5]
                if op == nextop == opmap["LOAD_CONST"] and lastop == opmap["COMPARE_OP"] and cmp_op[lastarg] in env.keys():
                    changed = True
                    result = True
                    last_opname = cmp_op[lastarg]
                    val = env[last_opname](fo.get_constant(arg), fo.get_constant(nextarg))
                    const_idx = fo.build_constant(val)
                    code[i], code[i + 1] = opmap["NOP"], 0
                    code[i + 2], code[i + 3] = opmap["NOP"], 0
                    code[i + 4], code[i + 5] = opmap["LOAD_CONST"], const_idx
    return result

def patch_const_binary_to_const(fo: CopyFunc) -> bool:
    # co: CopyCode, code: [int]
    co = fo["__code__"]
    code = co["codestring"]
    env = {
        opmap["BINARY_POWER"]           : operator.pow,
        opmap["BINARY_MULTIPLY"]        : operator.mul,
        opmap["BINARY_MATRIX_MULTIPLY"] : operator.matmul,
        opmap["BINARY_FLOOR_DIVIDE"]    : operator.floordiv,
        opmap["BINARY_TRUE_DIVIDE"]     : operator.truediv,
        opmap["BINARY_MODULO"]          : operator.mod,
        opmap["BINARY_ADD"]             : operator.add,
        opmap["BINARY_SUBTRACT"]        : operator.sub,
        opmap["BINARY_SUBSCR"]          : operator.getitem, # tuple support
        opmap["BINARY_LSHIFT"]          : operator.lshift,
        opmap["BINARY_RSHIFT"]          : operator.rshift,
        opmap["BINARY_AND"]             : operator.and_,
        opmap["BINARY_XOR"]             : operator.xor,
        opmap["BINARY_OR"]              : operator.or_,
    }
    length = len(code)
    changed = True
    result = False
    while changed:
        changed = False
        for i in range(0, length, 2):
            if i + 5 <= length:
                op, arg = code[i], code[i + 1]
                nextop, nextarg = code[i + 2], code[i + 3]
                lastop, lastarg = code[i + 4], code[i + 5]
                if op == nextop == opmap["LOAD_CONST"] and lastop in env.keys():
                    changed = True
                    result = True
                    val = env[lastop](fo.get_constant(arg), fo.get_constant(nextarg))
                    const_idx = fo.build_constant(val)
                    code[i], code[i + 1] = opmap["NOP"], 0
                    code[i + 2], code[i + 3] = opmap["NOP"], 0
                    code[i + 4], code[i + 5] = opmap["LOAD_CONST"], const_idx
    return True

def patch_merge_jump_absoulte(fo: CopyFunc) -> None:
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    for i in range(0, length, 2):
        if i + 3 < length:
            op, arg = code[i], code[i + 1]
            nextop, nextarg = code[i + 2], code[i + 3]
            if op == nextop == opmap["JUMP_ABSOLUTE"] and arg == nextarg:
                code[i], code[i + 1] = opmap["NOP"], 0

jump_target_collections = (
    opmap["POP_JUMP_IF_TRUE"],
    opmap["POP_JUMP_IF_FALSE"],
    opmap["JUMP_IF_TRUE_OR_POP"],
    opmap["JUMP_IF_FALSE_OR_POP"],
    opmap["JUMP_ABSOLUTE"],
    opmap["CONTINUE_LOOP"],
)
jump_delta_collections = (
    opmap["SETUP_WITH"],
    opmap["JUMP_FORWARD"],
    opmap["FOR_ITER"],
    opmap["SETUP_LOOP"],
    opmap["SETUP_EXCEPT"],
    opmap["SETUP_FINALLY"],
)
class NotSupportYet(Exception): pass

class Tag(object):
    def __init__(self, op: int):
        self.op = op
        self.to_mark = None
        self.be_marks = []
    def set_to_mark(self, label: str, type=True):
        # type = True is  jump target, label location is target
        # type = False is jump delta , label location is delta
        self.to_mark = (label, type)
    def set_be_marks(self, label: str, type=True):
        self.be_marks.append( (label, type) )
    def __repr__(self):
        return f"{{ {self.op} {self.to_mark} {self.be_marks} }}"

def collection_jump_label(fo: CopyFunc) -> None:
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    for i in range(0, length, 2):
        op, arg = code[i], code[i + 1]
        if op in jump_target_collections:
            label, type = label_id().hex, True

            source = Tag(op)
            source.set_to_mark(label, type)
            code[i] = source

            target_offset = arg
            target_op = code[target_offset]
            if not isinstance(target_op, Tag):
                target = Tag(target_op)
                target.set_be_marks(label, type)
                code[target_offset] = target
            else:
                target_op.set_be_marks(label, type)
        elif op in jump_delta_collections:
            label, type = label_id().hex, False

            source = Tag(op)
            source.set_to_mark(label, type)
            code[i] = source

            delta_offset = arg
            delta_op = code[i + delta_offset]
            if not isinstance(delta_op, Tag):
                target = Tag(delta_op)
                target.set_be_marks(label, type)
                code[i + delta_offset] = target
            else:
                delta_op.set_be_marks(label, type)
        elif isinstance(op, Tag):
            if op.op in jump_target_collections and op.to_mark is None:
                label, type = label_id().hex, True

                op.set_to_mark(label, type)

                target_offset = arg
                target_op = code[target_offset]
                if not isinstance(target_op, Tag):
                    target = Tag(target_op)
                    target.set_be_marks(label, type)
                    code[target_offset] = target
                else:
                    target_op.set_be_marks(label, type)

            elif op.op in jump_delta_collections and op.to_mark is None:
                label, type = label_id().hex, False

                op.set_to_mark(label, type)

                delta_offset = arg
                delta_op = code[i + delta_offset]
                if not isinstance(delta_op, Tag):
                    target = Tag(delta_op)
                    target.set_be_marks(label, type)
                    code[i + delta_offset] = target
                else:
                    delta_op.set_be_marks(label, type)

class InvaildKey(Exception): pass
def get_label_location(code: [object], key: (str, bool)) -> int:
    length = len(code)
    tags = [(i, code[i]) for i in range(0, length, 2) if isinstance(code[i], Tag)]
    for i, tag in tags:
        if key in tag.be_marks:
            tag.be_marks.remove(key)
            return i
    else:
        raise InvaildKey

def calculus_new_labels_location(code: [object]) -> [int]:
    length = len(code)
    for i in range(0, length, 2):
        op, arg = code[i], code[i + 1]
        if isinstance(op, Tag) and op.to_mark is not None: # is jump statement
            location = get_label_location(code, op.to_mark)
            # if not op.be_marks:
            # code[i] = op.op
            _, isTarget = op.to_mark
            op.to_mark = None
            if isTarget:
                target = location
                code[i + 1] = target
            else:
                delta = location - i
                code[i + 1] = delta
    for i in range(0, length, 2):
        op, arg = code[i], code[i + 1]
        if isinstance(op, Tag) and op.to_mark is None and not op.be_marks: # is jump statement
            code[i] = op.op

def clean_unused_local_name(fo: CopyFunc) -> None:
    co = fo["__code__"]
    code = co["codestring"]
    old_local_names = co["varnames"]
    new_local_names = []
    push = new_local_names.append
    length = len(code)
    for i in range(0, length, 2):
        op, arg = code[i], code[i + 1]
        if op in [opmap["LOAD_FAST"], opmap["STORE_FAST"], opmap["DELETE_FAST"]]:
            name = old_local_names[arg]
            if name not in new_local_names:
                push(name)
            idx = new_local_names.index(name)
            code[i + 1] = idx
    co["varnames"] = new_local_names

def clean_unused_const(fo: CopyFunc) -> None:
    co = fo["__code__"]
    code = co["codestring"]
    old_local_names = co["constants"]
    co["constants"] = []

    length = len(code)
    for i in range(0, length, 2):
        op, arg = code[i], code[i + 1]
        if op == opmap["LOAD_CONST"]:
            _, val = old_local_names[arg]
            idx = fo.build_constant(val)
            code[i + 1] = idx


def patch_jump_if(fo: CopyFunc) -> None:
    co = fo["__code__"]
    code = co["codestring"]
    length = len(code)
    # opmap["POP_JUMP_IF_TRUE"],
    # opmap["JUMP_IF_TRUE_OR_POP"],
    # opmap["JUMP_IF_FALSE_OR_POP"],
    modify = False
    for i in range(0, length, 2):
        if i + 3 <= length:
            op, arg = code[i], code[i + 1]
            nextop, nextarg = code[i + 2], code[i + 3]
            if op == opmap["LOAD_CONST"]:
                if nextop == opmap["POP_JUMP_IF_FALSE"]:
                    modify = True
                    val = fo.get_constant(arg)
                    target = nextarg
                    print( "[flag]", i, val )
                    if not val:
                        code[i], code[i + 1] = opmap["NOP"], 0
                        code[i + 2], code[i + 3] = opmap["NOP"], 0
                        for x in range(i, target, 2):
                            code[x], code[x + 1] = opmap["NOP"], 0
                            # print( opname[code[x]], code[x], code[x + 1] )
                    else:
                        code[i], code[i + 1] = opmap["NOP"], 0
                        code[i + 2], code[i + 3] = opmap["NOP"], 0
                        for x in range(target, length, 2):
                            code[x], code[x + 1] = opmap["NOP"], 0
                            # print( opname[code[x]], code[x], code[x + 1] )
                elif nextop == opmap["POP_JUMP_IF_TRUE"]:
                    modify = True
                    val = fo.get_constant(arg)
                    target = nextarg
                    print( "[flag]", i, val )
                    if val:
                        code[i], code[i + 1] = opmap["NOP"], 0
                        code[i + 2], code[i + 3] = opmap["NOP"], 0
                        for x in range(i, target, 2):
                            code[x], code[x + 1] = opmap["NOP"], 0
                            # print( opname[code[x]], code[x], code[x + 1] )
                    else:
                        code[i], code[i + 1] = opmap["NOP"], 0
                        code[i + 2], code[i + 3] = opmap["NOP"], 0
                        for x in range(target, length, 2):
                            code[x], code[x + 1] = opmap["NOP"], 0


    return modify

def simple_patch_drop_nop(fo: CopyFunc) -> None:
    # co: CopyCode, code: [int]
    changed = True
    while changed:
        patch_const_binary_to_const(fo)
        co = fo["__code__"]
        code = co["codestring"]
        labels = collection_jump_label(fo)
        length = len(code)
        codestring = []
        push = codestring.extend
        for i in range(0, length, 2):
            op, arg = code[i], code[i + 1]
            if isinstance(op, tuple):
                push((op, arg))
            else:
                if op != opmap["NOP"]:
                    push((op, arg))
        calculus_new_labels_location(codestring)
        co["codestring"] = codestring
        f_T = patch_const_build_tuple_to_const(fo)
        f_C = patch_const_compare_to_const(fo)
        changed = f_T or f_C

def patch(fo: CopyFunc) -> None:
    # constant binary to constant
    patch_const_binary_to_const(fo)

    # global ref const to const
    patch_global_const_to_const(fo)

    # local ref const to const
    patch_local_const_to_const(fo)

    # constant binary to constant
    patch_const_binary_to_const(fo)

    # merge continue at loop last
    patch_merge_jump_absoulte(fo)

    # convert const store to nop
    patch_const_store_to_nop(fo)

    # remove nop and recalculate jump label and location
    simple_patch_drop_nop(fo)
    while patch_jump_if(fo):
        simple_patch_drop_nop(fo)
    clean_unused_local_name(fo)
    clean_unused_const(fo)
