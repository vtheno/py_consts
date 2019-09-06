from optimization import optimization

def example(url):
    global ROOT    
    ROOT = ""
    SPLIT = "/"
    return url == ROOT + SPLIT + "url"

example_optimized = optimization(example)

def example2(url):
    return url == "/url"

example2_optimized = optimization(example)

from timeit import timeit
count = 1000000
print( "-" * 100 )

before = timeit("example('url')", "from __main__ import example", number=count)
after =  timeit("example_optimized('url')", "from __main__ import example_optimized", number=count)

print( f"before                     {before}" )
print( f"after                      {after}" )
print( f"after < before             {after < before}" )
print( f"before / after             {before / after}" )
print( f"example()                  {example('url')}" )
print( f"example_optimized()        {example_optimized('url')}" )
print( "-" * 100 )

before = timeit("example2('url')", "from __main__ import example2", number=count)
after =  timeit("example2_optimized('url')", "from __main__ import example2_optimized", number=count)

print( f"before                     {before}" )
print( f"after                      {after}" )
print( f"after < before             {after < before}" )
print( f"before / after             {before / after}" )
print( f"example2()                  {example2('url')}" )
print( f"example2_optimized()        {example2_optimized('url')}" )
print( "-" * 100 )