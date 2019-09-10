from optimization import optimization

@optimization
def if_statement():
    CONST = False
    if CONST:
        # ...
        return True
    return False

@optimization
def example():
    global ROOT    
    ROOT = "/"
    @optimization
    def _inline_example():
        print(ROOT)
    return _inline_example

import dis

dis.dis(example)