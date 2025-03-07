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

    def _get_value(self, a) -> int:
        return a if isinstance(a, int) else a.value

    def add(self, a, b) -> int:
        return (self._get_value(a) + self._get_value(b)) % self.order
    
    def mul(self, a, b) -> int:
        return (self._get_value(a) * self._get_value(b)) % self.order
    
    def sum(self, l) -> int:
        current_sum = 0
        for e in l:
            current_sum = self.add(current_sum, e)

        return current_sum

    
prime = 100000000003
FF = FiniteField(prime)