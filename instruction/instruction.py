from instruction.code import opmap
from instruction import code

from typing import Union, Any, List, Iterator, Tuple, Dict

class Label(object):
    def __init__(self, id: int):
        self.id = id
    def __repr__(self):
        return f"<Label {self.id}>"
    def __eq__(self, obj: Any):
        if isinstance(obj, self.__class__):
            return obj.id == self.id
        return False

class _Label(object):
    def __getitem__(self, arg: int):
        return Label(arg)

label = _Label()

class _Nothing(object):
    def __repr__(self):
        return ""

Nothing = _Nothing()

class Instruction(object):
    def __init__(self, op: Union[_Nothing, int], oparg: Any = Nothing, *, lineno=None):
        self.op = op
        self.oparg = oparg
    def __repr__(self):
        if self.oparg is Nothing:
            return f"{opmap[self.op]}"
        return f"{opmap[self.op]} {self.oparg}"
    def __iter__(self):
        return (self.op, self.oparg)
    def pack(self):
        if self.oparg is Nothing:
            return self.op, 0
        return self.op, self.oparg
    def replace(self, *, op: Union[_Nothing, int] = Nothing, oparg: Any = Nothing):
        if op is not Nothing:
            self.op = op
        if oparg is not Nothing:
            self.oparg = oparg

__all__ = [
    "Instruction",
    "label",
    "Nothing",
    "codelist",
]

class Const(object):
    def __init__(self, id: int, type: Any, value: Any):
        self.id = id
        self.type = type
        self.value = value
    def __repr__(self):
        return f"<Const {self.id} {self.type} {self.value}>"
    def __eq__(self, obj: Any):
        if isinstance(obj, self.__class__):
            return obj.id == self.id and obj.type == self.type and obj.value == self.value
        return False

def codelist(sequence: List[Any]) -> Tuple[Dict[int, int], List[Any], List[str], List[int]]:
    labels = {}
    # label collection
    for addr, instr in enumerate(sequence):
        if isinstance(instr, tuple):
            label, real_instr = instr
            sequence[addr] = real_instr
            real_addr = addr + addr
            labels[label.id] = real_addr
    # jump label to instance
    target_jumps = (
        code.POP_JUMP_IF_TRUE,
        code.POP_JUMP_IF_FALSE,
        code.JUMP_IF_TRUE_OR_POP,
        code.JUMP_IF_FALSE_OR_POP,
        code.JUMP_ABSOLUTE,
    )
    delta_jumps = (
        code.SETUP_WITH,
        code.JUMP_FORWARD,
        code.FOR_ITER,
        code.SETUP_FINALLY,
        code.CALL_FINALLY,
    )
    for addr, instr in enumerate(sequence):
        if instr.op in target_jumps and isinstance(instr.oparg, Label):
            instr.replace(oparg=labels[instr.oparg.id])
        if instr.op in delta_jumps and isinstance(instr.oparg, Label):
            real_addr = addr + 1
            real_addr += real_addr
            instr.replace(oparg=labels[instr.oparg.id] - real_addr)
    
    consts: List[Const] = []
    # const collection
    for instr in sequence:
        if instr.op == code.LOAD_CONST and not isinstance(instr.oparg, Const):
            val = instr.oparg
            const = Const(id(val), type(val), val)
            if const not in consts:
                consts.append(const)
            instr.replace(oparg=const)
    # Const to consti
    for instr in sequence:
        if instr.op == code.LOAD_CONST and isinstance(instr.oparg, Const):
            consti = consts.index(instr.oparg)
            instr.replace(oparg=consti)

    # varnames collection and varname to varnamei
    varnames: List[str] = []
    about_fast_op: Tuple[int, int, int] = (
        code.LOAD_FAST, code.STORE_FAST, code.DELETE_FAST, 
    )
    for instr in sequence:
        if instr.op in about_fast_op and isinstance(instr.oparg, str):
            varname = instr.oparg
            if varname not in varnames:
                varnames.append(varname)
            varnamei = varnames.index(varname)
            instr.replace(oparg=varnamei)

    names: List[str] = []    
    # names collection and name to namei
    about_name_op: Tuple[
        int, int, int,
        int, int, int,
        int, int, int,
        int, int,
        int,
    ] = (
        code.LOAD_NAME, code.STORE_NAME, code.DELETE_NAME,
        code.LOAD_ATTR, code.STORE_ATTR, code.DELETE_ATTR, 
        code.LOAD_GLOBAL, code.STORE_GLOBAL, code.DELETE_GLOBAL,
        code.IMPORT_NAME, code.IMPORT_FROM,
        code.LOAD_METHOD,
    )
    # TODO etc ...
    for instr in sequence:
        if instr.op in about_name_op and isinstance(instr.oparg, str):
            name = instr.oparg
            if name not in names:
                names.append(name)
            namei = names.index(name)
            instr.replace(oparg=namei)
    # freevars
    freevars: List[str] = []
    # 
    # cellvars
    cellvars: List[str] = []
    # LOAD_CLOSURE
    for instr in sequence:
        if instr.op == code.LOAD_CLOSURE and isinstance(instr.oparg, str):
            cell_varname = instr.oparg
            if cell_varname not in cellvars:
                cellvars.append(cell_varname)
            cell_varnamei = cellvars.index(cell_varname)
            instr.replace(oparg=cell_varnamei)
    
    return labels, consts, names, sequence