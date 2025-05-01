"""
Skeleton credential module for implementing PS credentials

The goal of this skeleton is to help you implementing PS credentials. Following
this API is not mandatory and you can change it as you see fit. This skeleton
only provides major functionality that you will need.

You will likely have to define more functions and/or classes. In particular, to
maintain clean code, we recommend to use classes for things that you want to
send between parties. You can then use `jsonpickle` serialization to convert
these classes to byte arrays (as expected by the other classes) and back again.

We also avoided the use of classes in this template so that the code more closely
resembles the original scheme definition. However, you are free to restructure
the functions provided to resemble a more object-oriented interface.
"""

from typing import Any, List, Tuple, NamedTuple

from serialization import jsonpickle

from petrelic.multiplicative.pairing import G1, G2, GT, G1Element, G2Element
from math import gcd


# Type hint aliases
# Feel free to change them as you see fit.
# Maybe at the end, you will not need aliases at all!
class SecretKey(NamedTuple):
    x: int
    X: G1Element
    y: List[int]

class PublicKey(NamedTuple):
    g: G1Element
    Y: List[G1Element]
    g_tilde: G2Element
    X_tilde: G2Element
    Y_tilde: List[G2Element]

Signature = Tuple[G1Element, G1Element]
Attribute = Any
AttributeMap = Any
IssueRequest = Any
BlindSignature = Any
AnonymousCredential = Any
DisclosureProof = Any


######################
## SIGNATURE SCHEME ##
######################

def random_generator(group, generator):
    """ Generate a random cyclic group generator based on a fixed generator """
    n = int(group.order())
    exp = group.order().random()
    while gcd(exp, n) != 1:
        exp = group.order().random()

    return generator ** exp


def generate_key(
        attributes: List[Attribute]
    ) -> Tuple[SecretKey, PublicKey]:
    """ Generate signer key pair """
    L = len(attributes)

    x = int(G1.order().random())
    y = []
    for i in range(L):
        y.append(int(G1.order().random()))

    g = random_generator(G1, G1.generator())
    g_tilde = random_generator(G2, G2.generator())

    X = g ** x
    X_tilde = g_tilde ** x

    Y = []
    Y_tilde = []
    for i in range(L):
        Y.append(g ** y[i])
        Y_tilde.append(g_tilde ** y[i])

    return PublicKey(g, y, g_tilde, X_tilde, Y_tilde), SecretKey(x, X, y)


def sign(
        sk: SecretKey,
        msgs: List[bytes]
    ) -> Signature:
    """ Sign the vector of messages `msgs` """
    L = len(msgs)

    h = random_generator(G1, G1.generator())
    exp2 = sk.x
    for i in range(L):
        exp2 += sk.y[i] * int.from_bytes(msgs[i], "big")

    return (h, h ** exp2)


def verify(
        pk: PublicKey,
        signature: Signature,
        msgs: List[bytes]
    ) -> bool:
    """ Verify the signature on a vector of messages """
    if signature[0].is_neutral_element():
        return False
    
    L = len(msgs)

    # Left hand side
    prod = pk.X_tilde
    for i in range(L):
        prod *= pk.Y_tilde[i] ** int.from_bytes(msgs[i], "big")

    lhs = signature[0].pair(prod)

    # Right hand side
    rhs = signature[1].pair(pk.g_tilde)
    
    return lhs == rhs


#################################
## ATTRIBUTE-BASED CREDENTIALS ##
#################################

## ISSUANCE PROTOCOL ##

def create_issue_request(
        pk: PublicKey,
        user_attributes: AttributeMap
    ) -> IssueRequest:
    """ Create an issuance request

    This corresponds to the "user commitment" step in the issuance protocol.

    *Warning:* You may need to pass state to the `obtain_credential` function.
    """
    raise NotImplementedError()


def sign_issue_request(
        sk: SecretKey,
        pk: PublicKey,
        request: IssueRequest,
        issuer_attributes: AttributeMap
    ) -> BlindSignature:
    """ Create a signature corresponding to the user's request

    This corresponds to the "Issuer signing" step in the issuance protocol.
    """
    raise NotImplementedError()


def obtain_credential(
        pk: PublicKey,
        response: BlindSignature
    ) -> AnonymousCredential:
    """ Derive a credential from the issuer's response

    This corresponds to the "Unblinding signature" step.
    """
    raise NotImplementedError()


## SHOWING PROTOCOL ##

def create_disclosure_proof(
        pk: PublicKey,
        credential: AnonymousCredential,
        hidden_attributes: List[Attribute],
        message: bytes
    ) -> DisclosureProof:
    """ Create a disclosure proof """
    raise NotImplementedError()


def verify_disclosure_proof(
        pk: PublicKey,
        disclosure_proof: DisclosureProof,
        message: bytes
    ) -> bool:
    """ Verify the disclosure proof

    Hint: The verifier may also want to retrieve the disclosed attributes
    """
    raise NotImplementedError()
