from optimization import optimization

def example(url):
    global ROOT
    ROOT = ""
    SPLIT = "/"
    if ROOT + SPLIT + "url":
        return "prefix" + "/" + url
    return url
import dis

dis.dis(example)
print( "-" * 100 )
example_optimized = optimization(example)
dis.dis(example_optimized)


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
