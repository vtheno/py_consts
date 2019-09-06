from meta import CopyFunc
from meta import patch_global_const_to_const
from meta import patch_local_const_to_const
from meta import patch_const_store_to_nop
from meta import patch_const_binary_to_const
from meta import patch_merge_jump_absoulte
from meta import collection_jump_label
from meta import simple_patch_drop_nop

import dis

def pprint(codestring):
    for i in range(0, len(codestring), 2):
        print( i, codestring[i], codestring[i + 1] )

def optimization(f):
    dis.dis(f)
    print("-"*100)
    fo = CopyFunc(f)
    
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
    f = fo.build()
    dis.dis(f)
    print("-"*100)
    fo = CopyFunc(f)
    # remove nop and recalculate jump label and location
    simple_patch_drop_nop(fo)
    
    pprint(fo["__code__"]["codestring"])
    print("-"*100)    

    return fo.build() 



def example():
    global a, b, c, d, e, f
    a = 1 + 2                       # 3
    b = a + 1                       # 4
    c = b + 1                       # 5
    d = c + 1                       # 6
    e = a * b * c / d               # 10.0
    f = (e, d, c, b)                # (10.0, 6, 5, 4)
    if a < b:                       # if 3 < 4
        h = f                       # h = (10.0, 6, 5, 4)
        count = e                   # count = 10.0
        Sum = 0                     # Sum = 0
        for x in range(int(count)): # for x in range(int(10.0))
            Sum += x                # Sum += x
            continue                # continue
        return Sum, h               # return Sum, (10.0, 6, 5, 4)
    else:                           # else
        return 0, f                 # return 0, (10.0, 6, 5, 4)

test = optimization(example)
dis.dis(test)
print("-"*100)

#"""
from timeit import timeit
count = 1

before = timeit("example()", "from __main__ import example", number=count)
after =  timeit("test()", "from __main__ import test", number=count)

print( f"before             {before}" )
print( f"after              {after}" )
print( f"after < before     {after < before}" )
print( f"before / after     {before / after}" )
print( f"test()             {test()}" )
print( f"example()          {example()}" )
#"""