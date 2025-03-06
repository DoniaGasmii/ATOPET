from typing import Iterable

class FiniteField:
    """
    Implemented as a singleton because all parties must do arithmetic in the same finite field
    """
    _instance = None

    def __new__(cls, order):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.order = order
        return cls._instance

    def add(self, a, b) -> int:
        a_val = a if isinstance(a, int) else a.value
        b_val = b if isinstance(b, int) else b.value
        return (a_val + b_val) % self.order
    
    def mul(self, a, b) -> int:
        a_val = a if isinstance(a, int) else a.value
        b_val = b if isinstance(b, int) else b.value
        return (a_val * b_val) % self.order
    
    def sum(self, l) -> int:
        current_sum = 0
        for e in l:
            current_sum = self.add(current_sum, e)

        return current_sum

    
prime = 1000000007
FF = FiniteField(prime)