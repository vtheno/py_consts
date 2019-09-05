from meta import CopyFunc
from meta import patch_global_const_to_const
from meta import patch_local_const_to_const
from meta import patch_const_store_to_nop
from meta import patch_const_binary_to_const
from meta import simple_patch_drop_nop
import dis


def optimization(f):
    
    fo = CopyFunc(f)
    
    # constant binary to constant
    patch_const_binary_to_const(fo)

    # global ref const to const    
    patch_global_const_to_const(fo) 
    
    # local ref const to const
    patch_local_const_to_const(fo)

    # constant binary to constant
    patch_const_binary_to_const(fo)

    patch_const_store_to_nop(fo)   
    simple_patch_drop_nop(fo) # no calculus loop statement, if statement, try statement

    return fo.build() 

def example(g=0):
    global a
    a = 1 + 2
    b = a + 1
    c = b + 1
    d = c + 1
    e = a  * b * c / d
    f = (e, e, e)
    return f[2], g

test = optimization(example)


dis.dis(example)
print("-"*100)
dis.dis(test)
print("-"*100)

from timeit import timeit
count = 1000000

after =  timeit("test()", "from __main__ import test", number=count)
before = timeit("example()", "from __main__ import example", number=count)

print( f"before             {before}" )
print( f"after              {after}" )
print( f"after < before     {after < before}" )
print( f"before / after     {before / after}" )
print( f"test()             {test()}" )
print( f"example()          {example()}" )