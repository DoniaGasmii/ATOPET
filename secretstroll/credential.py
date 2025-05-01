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

from typing import Any, List, Tuple, NamedTuple, Dict

from serialization import jsonpickle

from petrelic.multiplicative.pairing import G1, G2, GT, G1Element, G2Element
from math import gcd # for random generator generation
from hashlib import shake_256 # for arbitrary output size hash output, to avoid statistical bias from fixed output size hashes


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
Attribute = int
AttributeMap = Dict[int, Attribute]
class IssueRequest(NamedTuple):
    C: G1Element
    pi: Any

class CommitmentProof(NamedTuple):
    T: G1Element
    k: int
    s0: int
    ts: Dict[int, int]

BlindSignature = Signature # I don't really see the difference regarding types
AnonymousCredential = Signature # Same here
DisclosureProof = Any


######################
## SIGNATURE SCHEME ##
######################

def random_generator(group, generator):
    """ Generate a random cyclic group generator based on a fixed generator """
    n = group.order()
    exp = group.order().random()
    while gcd(exp, n) != 1:
        exp = group.order().random()

    return generator ** exp


def generate_key(
        attributes: List[Attribute]
    ) -> Tuple[SecretKey, PublicKey]:
    """ Generate signer key pair """
    L = len(attributes)

    x = G1.order().random()
    y = []
    for i in range(L):
        y.append(G1.order().random())

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
    t = G1.order().random()
    C = pk.g ** t
    print("asdfasdfasdf")
    print(user_attributes)
    for attribute in user_attributes:
        print(user_attributes[attribute])
        C *= pk.Y[attribute] ** user_attributes[attribute]

    # ZKP
    t0 = G1.order().random()
    ts = dict()
    T = pk.g ** t0
    for attribute in user_attributes:
        current_t = G1.order().random()
        ts[attribute] = current_t
        T *= pk.Y[attribute] ** current_t
    
    k = shake_256(f"{g}{[(attribute, pk.Y[attribute]) for attribute in user_attributes]}{C}{T}").digest(int(G1.order()).bit_length() + 1) % G1.order()

    s0 = (k * t + t0) % G1.order()
    for elem in ts:
        ts[elem] = (k * user_attributes[elem] + ts[elem]) % G1.order()

    pi = CommitmentProof(T, k, s0, ts)

    # We need to return t so it can be used in obtain_credential,
    # but it should not be sent to the issuer.
    return IssueRequest(C, pi), t


def sign_issue_request(
        sk: SecretKey,
        pk: PublicKey,
        request: IssueRequest,
        issuer_attributes: AttributeMap
    ) -> BlindSignature:
    """ Create a signature corresponding to the user's request

    This corresponds to the "Issuer signing" step in the issuance protocol.
    """
    # Verify request ZKP
    prod = pk.g ** request.pi.s0
    for attribute in request.pi.ts:
        prod *= pk.Y[attribute] ** request.pi.ts[attribute]

    prod *= request.pi.T

    assert prod == request.C ** request.pi.k

    # Sign
    u = G1.order().random()

    left = pk.g ** u

    right = sk.X * request.C
    for attribute in issuer_attributes:
        right *= pk.Y[attribute] ** issuer_attributes[attribute]

    right **= u

    return BlindSignature(left, right), issuer_attributes


def obtain_credential(
        pk: PublicKey,
        response: BlindSignature,
        t: int
    ) -> AnonymousCredential:
    """ Derive a credential from the issuer's response

    This corresponds to the "Unblinding signature" step.
    """
    return (response[0], response[1] * (response[0].inverse() ** t))


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
