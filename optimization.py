from meta import CopyFunc
from meta import patch

__all__ = ['optimization']
def optimization(f):
    fo = CopyFunc(f)
    patch(fo)
    return fo.build()
