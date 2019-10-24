def to_bin(x: int, n: int = 16) -> str:
    """
    x: int
    n: int ; bit wide
    """
    return format(x, 'b').zfill(n)

def to_int(b: str) -> int:
    """
    b: str ; binary string
    """
    return int(b, 2)

__all__ = [
    "to_bin", "to_int"
]