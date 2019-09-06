from meta import CopyFunc
from meta import patch_global_const_to_const
from meta import patch_local_const_to_const
from meta import patch_const_store_to_nop
from meta import patch_const_binary_to_const
from meta import patch_merge_jump_absoulte
from meta import collection_jump_label
from meta import simple_patch_drop_nop

__all__ = ['optimization']
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

    # merge continue at loop last
    patch_merge_jump_absoulte(fo)

    # convert const store to nop
    patch_const_store_to_nop(fo)

    # remove nop and recalculate jump label and location
    simple_patch_drop_nop(fo)

    return fo.build() 