"""
Secret sharing scheme.
"""

from __future__ import annotations

import json
import random
from typing import List

from finite_field import FF


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, value):
        # Adapt constructor arguments as you wish
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __add__(self, other):
        return Share(self.value + other.value)

    def __sub__(self, other):
        return Share(self.value - other.value)

    def __mul__(self, other):
        return Share(self.value * other.value)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json.dumps({"value": self.value})

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        data = json.loads(serialized)
        return Share(data["value"])

def share_secret(secret: int, num_shares: int) -> List[Share]:
    shares = [Share(random.randint(0, FF.order)) for _ in range(num_shares - 1)]
    shares.append(Share(FF.sub(secret, FF.sum(shares))))
    return shares

def reconstruct_secret(shares: List[Share]) -> int:
    return sum(shares)