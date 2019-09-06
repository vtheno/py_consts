from optimization import optimization

def contains():
    a = 1
    b = 2
    c = 3
    d = (a, b, c)
    e = 2
    return (e in d, e not in d)

contains_optimized = optimization(contains)
import dis
dis.dis(contains_optimized)

from timeit import timeit
count = 1000000
print( "-" * 100 )

before = timeit("contains()", "from __main__ import contains", number=count)
after =  timeit("contains_optimized()", "from __main__ import contains_optimized", number=count)

print( f"before                     {before}" )
print( f"after                      {after}" )
print( f"after < before             {after < before}" )
print( f"before / after             {before / after}" )
print( f"contains()                 {contains()}" )
print( f"contains_optimized()       {contains_optimized()}" )
print( "-" * 100 )
