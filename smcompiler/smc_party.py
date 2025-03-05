"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Expression,
    Secret, Scalar, Addition, Multiplication
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int],
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict
        self.lead = client_id == protocol_spec.participant_ids[0]


    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        for k in self.value_dict.keys():
            l = share_secret(self.value_dict.get(k), len(self.protocol_spec.participant_ids))

            i = 0
            for client in self.protocol_spec.participant_ids:
                self.comm.send_private_message(client, str(k.id.__hash__()), l[i].serialize())
                i = i + 1

        #process main
        res = self.process_expression(self.protocol_spec.expr)
        self.comm.publish_message("result", res.serialize())
        final_shares = []
        for client in self.protocol_spec.participant_ids:
            final_shares.append(Share.deserialize(self.comm.retrieve_public_message(client, "result")))
        return sum(final_shares, Share(0)).value


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):

        if isinstance(expr, Secret):
            buf = self.comm.retrieve_private_message(str(expr.id.__hash__()))
            val = Share.deserialize(buf)
            return val
        elif isinstance(expr, Scalar):
            return expr
        elif isinstance(expr, Addition):
            resA = self.process_expression(expr.a)
            resB = self.process_expression(expr.b)

            if ((isinstance(resA, Scalar) or isinstance(resB, Scalar)) and self.lead)\
                    or (isinstance(resA, Share) and isinstance(resB, Share)):
                return resA+resB

            else:
                if isinstance(resA, Scalar):
                    return resB
                else:
                    return resA

        elif isinstance(expr, Multiplication):
            #TODO
            raise NotImplementedError
        else:
            raise ValueError("Unknown expression type")
