from instruction.instruction import Instruction
from instruction import code
__all__ = ["stacksize"]
def stacksize(instr: Instruction) -> int:
	if not isinstance(instr.oparg, int):
		raise TypeError("stacksize(instr: Instruction) require instr.oparg type is int")
	if instr.op == code.POP_TOP: 
		return -1
	if instr.op == code.ROT_TWO: 
		return 0
	if instr.op == code.ROT_THREE: 
		return 0
	if instr.op == code.DUP_TOP: 
		return 1
	if instr.op == code.DUP_TOP_TWO: 
		return 2
	if instr.op == code.ROT_FOUR: 
		return 0
	if instr.op == code.NOP: 
		return 0
	if instr.op == code.UNARY_POSITIVE: 
		return 0
	if instr.op == code.UNARY_NEGATIVE: 
		return 0
	if instr.op == code.UNARY_NOT: 
		return 0
	if instr.op == code.UNARY_INVERT: 
		return 0
	if instr.op == code.BINARY_MATRIX_MULTIPLY: 
		return -1
	if instr.op == code.INPLACE_MATRIX_MULTIPLY: 
		return -1
	if instr.op == code.BINARY_POWER: 
		return -1
	if instr.op == code.BINARY_MULTIPLY: 
		return -1
	if instr.op == code.BINARY_MODULO: 
		return -1	
	if instr.op == code.BINARY_ADD: 
		return -1	
	if instr.op == code.BINARY_SUBTRACT: 
		return -1	
	if instr.op == code.BINARY_SUBSCR: 
		return -1
	if instr.op == code.BINARY_FLOOR_DIVIDE: 
		return -1
	if instr.op == code.BINARY_TRUE_DIVIDE: 
		return -1
	if instr.op == code.INPLACE_FLOOR_DIVIDE: 
		return -1
	if instr.op == code.INPLACE_TRUE_DIVIDE: 
		return -1
	if instr.op == code.GET_AITER: 
		return 0
	if instr.op == code.GET_ANEXT: 
		return 1
	if instr.op == code.BEFORE_ASYNC_WITH: 
		return 1
	if instr.op == code.BEGIN_FINALLY: 
		return 6
	if instr.op == code.END_ASYNC_FOR: 
		return -7
	if instr.op == code.INPLACE_ADD: 
		return -1
	if instr.op == code.INPLACE_SUBTRACT: 
		return -1
	if instr.op == code.INPLACE_MULTIPLY: 
		return -1
	if instr.op == code.INPLACE_MODULO: 
		return -1
	if instr.op == code.STORE_SUBSCR: 
		return -3
	if instr.op == code.DELETE_SUBSCR: 
		return -2
	if instr.op == code.BINARY_LSHIFT: 
		return -1
	if instr.op == code.BINARY_RSHIFT: 
		return -1
	if instr.op == code.BINARY_AND: 
		return -1
	if instr.op == code.BINARY_XOR: 
		return -1
	if instr.op == code.BINARY_OR: 
		return -1
	if instr.op == code.INPLACE_POWER: 
		return -1
	if instr.op == code.GET_ITER: 
		return 0
	if instr.op == code.GET_YIELD_FROM_ITER: 
		return 0
	if instr.op == code.PRINT_EXPR: 
		return -1
	if instr.op == code.LOAD_BUILD_CLASS: 
		return 1
	if instr.op == code.YIELD_FROM: 
		return -1
	if instr.op == code.GET_AWAITABLE: 
		return 0
	if instr.op == code.INPLACE_LSHIFT: 
		return -1
	if instr.op == code.INPLACE_RSHIFT: 
		return -1
	if instr.op == code.INPLACE_AND: 
		return -1
	if instr.op == code.INPLACE_XOR: 
		return -1
	if instr.op == code.INPLACE_OR: 
		return -1
	if instr.op == code.WITH_CLEANUP_START: 
		return 2
	if instr.op == code.WITH_CLEANUP_FINISH: 
		return -3
	if instr.op == code.RETURN_VALUE: 
		return -1
	if instr.op == code.IMPORT_STAR: 
		return -1
	if instr.op == code.SETUP_ANNOTATIONS: 
		return 0
	if instr.op == code.YIELD_VALUE: 
		return 0
	if instr.op == code.POP_BLOCK: 
		return 0
	if instr.op == code.END_FINALLY: 
		return -6
	if instr.op == code.POP_EXCEPT: 
		return -3
	if instr.op == code.STORE_NAME: 
		return -1
	if instr.op == code.DELETE_NAME: 
		return 0
	if instr.op == code.UNPACK_SEQUENCE: 
		return instr.oparg - 1
	if instr.op == code.FOR_ITER: 
		return 1
	if instr.op == code.UNPACK_EX: 
		return instr.oparg
	if instr.op == code.STORE_ATTR: 
		return -2
	if instr.op == code.DELETE_ATTR: 
		return -1
	if instr.op == code.STORE_GLOBAL: 
		return -1
	if instr.op == code.DELETE_GLOBAL: 
		return 0
	if instr.op == code.LOAD_CONST: 
		return 1
	if instr.op == code.LOAD_NAME: 
		return 1
	if instr.op == code.BUILD_TUPLE: 
		return -1 * instr.oparg + 1
	if instr.op == code.BUILD_LIST: 
		return -1 * instr.oparg + 1
	if instr.op == code.BUILD_SET: 
		return -1 * instr.oparg + 1
	if instr.op == code.BUILD_MAP: 
		return -2 * instr.oparg + 1
	if instr.op == code.LOAD_ATTR: 
		return 0
	if instr.op == code.COMPARE_OP: 
		return -1
	if instr.op == code.IMPORT_NAME: 
		return -1
	if instr.op == code.IMPORT_FROM: 
		return 1
	if instr.op == code.JUMP_FORWARD: 
		return 0
	if instr.op == code.JUMP_IF_FALSE_OR_POP: # pop or non-pop  choice max
		return 0
	if instr.op == code.JUMP_IF_TRUE_OR_POP: 
		return 0
	if instr.op == code.JUMP_ABSOLUTE: 
		return 0
	if instr.op == code.POP_JUMP_IF_FALSE: 
		return -1
	if instr.op == code.POP_JUMP_IF_TRUE: 
		return -1
	if instr.op == code.LOAD_GLOBAL: 
		return 1
	if instr.op == code.SETUP_FINALLY: 
		return 6
	if instr.op == code.LOAD_FAST: 
		return 1
	if instr.op == code.STORE_FAST: 
		return -1
	if instr.op == code.DELETE_FAST: 
		return 0
	if instr.op == code.RAISE_VARARGS: 
		return -1 * instr.oparg
	if instr.op == code.CALL_FUNCTION: 
		return -1 * instr.oparg
	if instr.op == code.MAKE_FUNCTION: 
		if instr.oparg < 0:
			raise ValueError("MAKE_FUNCTION argc require not negative")
		total = 0
		binary = format(instr.oparg, 'b').zfill(4)
		# 0x01  0x02  0x04  0x08
		# 0001  0010  0100  1000
		if binary[0] == '1':
			total -= 1
		if binary[1] == '1':
			total -= 1
		if binary[2] == '1':
			total -= 1
		if binary[3] == '1':
			total -= 1
		total -= 1 # code at TOS1
		total -= 1 # qualified name at TOS
		total += 1 # push function back
		return total
	if instr.op == code.BUILD_SLICE: 
		total = 0
		if instr.oparg not in (2, 3):
			raise ValueError("BUILD_SLICE argc choice 2 or 3")
		if instr.oparg == 2: # slice(TOS1, TOS)
			total -= 1 # pop TOS1
			total -= 1 # pop TOS
		else: # slice(TOS2, TOS1, TOS)
			total -= 1 # pop TOS2
			total -= 1 # pop TOS1
			total -= 1 # pop TOS
		# push value back
		total += 1
		return total
	if instr.op == code.LOAD_CLOSURE: 
		return 1
	if instr.op == code.LOAD_DEREF: 
		return 1
	if instr.op == code.STORE_DEREF: 
		return -1
	if instr.op == code.DELETE_DEREF: 
		return 0
	if instr.op == code.CALL_FUNCTION_KW: 
		return -1 * instr.oparg	- 1
	if instr.op == code.CALL_FUNCTION_EX: 
		# flags	
		raise NotImplementedError
	if instr.op == code.SETUP_WITH: 
		raise NotImplementedError
	if instr.op == code.LIST_APPEND: 
		raise NotImplementedError
	if instr.op == code.SET_ADD: 
		raise NotImplementedError
	if instr.op == code.MAP_ADD: 
		raise NotImplementedError
	if instr.op == code.LOAD_CLASSDEREF: 
		raise NotImplementedError
	if instr.op == code.EXTENDED_ARG: 
		return 0
	if instr.op == code.BUILD_LIST_UNPACK: 
		raise NotImplementedError
	if instr.op == code.BUILD_MAP_UNPACK: 
		raise NotImplementedError
	if instr.op == code.BUILD_MAP_UNPACK_WITH_CALL: 
		raise NotImplementedError
	if instr.op == code.BUILD_TUPLE_UNPACK: 
		raise NotImplementedError
	if instr.op == code.BUILD_SET_UNPACK: 
		raise NotImplementedError
	if instr.op == code.SETUP_ASYNC_WITH: 
		raise NotImplementedError
	if instr.op == code.FORMAT_VALUE: 
		if instr.oparg < 0:
			raise ValueError("FORMAT_VALUE flags require not negative")
		total = -1	# pop an fmt_spec
		flags = format(instr.oparg, 'b').zfill(4)
		require_fmt_spec_again = format(0x04, 'b').zfill(4)
		result = ''.join('1' if f == r == '1' else '0' for f, r in zip(flags, require_fmt_spec_again))
		if result == require_fmt_spec_again:
			total = total - 1
		total = total + 1 # PyObject_Format() will push
		return total
	if instr.op == code.BUILD_CONST_KEY_MAP: 
		return -1 * instr.oparg
	if instr.op == code.BUILD_STRING: 
		return -1 * instr.oparg + 1	
	if instr.op == code.BUILD_TUPLE_UNPACK_WITH_CALL: 
		raise NotImplementedError
	if instr.op == code.LOAD_METHOD: 
		raise NotImplementedError
	if instr.op == code.CALL_METHOD: 
		raise NotImplementedError
	if instr.op == code.CALL_FINALLY: 
		raise NotImplementedError
	if instr.op == code.POP_FINALLY: 
		raise NotImplementedError