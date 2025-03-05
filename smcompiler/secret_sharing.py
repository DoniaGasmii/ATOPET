"""
Secret sharing scheme.
"""

from __future__ import annotations

import json
import random
from typing import List


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
    # TODO: finite field check
    shares = []
    for i in range(num_shares-1):
        shares.append(Share(random.randint(0, secret//num_shares)))
    shares.append(Share(secret) - sum(shares, Share(0)))

    """
    with finite field should be something like
    shares = []
    current_sum = 0
    for i in range(num_shares-1):
        shares.append(Share(random.randint(0, finite_field.order)))
        current_sum += shares[-1]
        current_sum %= finite_field.order # assuming finite field == integers modulo p

    if current_sum < secret:
        shares.append(Share(secret - current_sum))
    else:
        shares.append(Share(finite_field.order - current_sum + secret))
    """
    return shares

def reconstruct_secret(shares: List[Share]) -> int:
    return sum(shares)