"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import json
import random
from typing import Optional

from secret_sharing import Share

ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
        ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        return Addition(self, other)


    def __sub__(self, other):
        return Subtraction(self, other)


    def __mul__(self, other):
        return Multiplication(self, other)


    def __hash__(self):
        return hash(self.id)

class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
        ):
        self.value = value
        super().__init__(id)


    def __repr__(self):
        id_str = self.id.decode() if isinstance(self.id, bytes) else str(self.id)
        return f"{self.__class__.__name__}(id={id_str}, value={self.value if self.value is not None else ''})"

    def __hash__(self):
        return

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json.dumps({"value": self.value})

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        data = json.loads(serialized)
        return Share(data["value"])


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
            self,
            value: Optional[Share] = None,
            id: Optional[bytes] = None,
    ):
        super().__init__(id)
        self.value = value


    def __repr__(self):
        id_str = self.id.decode() if isinstance(self.id, bytes) else str(self.id)
        return f"{self.__class__.__name__}(id={id_str}, value={self.value if self.value is not None else ''})"

class Addition(Expression):
    def __init__(self, a: Expression, b: Expression, id: Optional[bytes] = None):
        super().__init__(id)
        self.a = a
        self.b = b

    def __repr__(self):
        return f"({self.a} + {self.b})"

class Subtraction(Expression):
    def __init__(self, a: Expression, b: Expression, id: Optional[bytes] = None):
        super().__init__(id)
        self.a = a
        self.b = b

    def __repr__(self):
        return f"({self.a} - {self.b})"

class Multiplication(Expression):
    def __init__(self, a: Expression, b: Expression, id: Optional[bytes] = None):
        super().__init__(id)
        self.a = a
        self.b = b

    def __repr__(self):
        return f"({self.a} * {self.b})"