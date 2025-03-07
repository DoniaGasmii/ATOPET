"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

import collections
from typing import (
    Dict,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import(
    share_secret,
    Share,
)

import random
from finite_field import FF

# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.stored_shares: Dict[str, Dict[str, Share]] = dict()


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        # If it's the first time the TTP receives a request for that operation id, it has to generate the shares first
        if op_id not in self.stored_shares:
            self._generate_shares(op_id)
        
        return self.stored_shares[op_id][client_id]
    
    def _generate_shares(self, op_id: str) -> None:
        a, b = random.randint(0, FF.order), random.randint(0, FF.order)
        c = FF.mul(a, b)

        a_shares, b_shares, c_shares = [share_secret(x, len(self.participant_ids)) for x in (a, b, c)]

        self.stored_shares[op_id] = dict(zip(self.participant_ids, zip(a_shares, b_shares, c_shares)))


    # Feel free to add as many methods as you want.
