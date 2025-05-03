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

from petrelic.multiplicative.pairing import G1, G2, GT, G1Element, G2Element, GTElement
from math import gcd # for random generator generation
from hashlib import shake_256 # for arbitrary output size hash output, to avoid statistical bias from fixed output size hashes


# Type hint aliases
# Feel free to change them as you see fit.
# Maybe at the end, you will not need aliases at all!
GElement = G1Element | G2Element | GTElement

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
    T: GElement
    k: int
    s0: int
    ts: Dict[int, int]

BlindSignature = Signature # I don't really see the difference regarding types

class AnonymousCredential(NamedTuple):
    signature: Signature
    attributes: AttributeMap

class DisclosureProof(NamedTuple):
    signature: Signature
    disclosed_attributes: AttributeMap
    pi: CommitmentProof

######################
## HELPER FUNCTIONS ##
######################

def random_generator(
        group,
        generator: GElement
    ) -> GElement:
    """ Generate a random cyclic group generator based on a fixed generator """
    n = group.order()
    exp = group.order().random()
    while gcd(exp, n) != 1:
        exp = group.order().random()

    return generator ** exp


def nizkp(
        basis: Tuple[GElement, List[GElement]],
        C: GElement,
        t: int,
        attributes: AttributeMap
    ) -> CommitmentProof:
    """ Compute non-interactive zero-knowledge proof of knowledge of secrets t and attributes """
    # ZKP
    t0 = G1.order().random()
    ts = dict()
    T = basis[0] ** t0
    for attr_key in attributes:
        current_t = G1.order().random()
        ts[attr_key] = current_t
        T *= basis[1][attr_key] ** current_t
    
    string_to_hash = f"{basis[0]}{[(attr_key, basis[1][attr_key]) for attr_key in attributes]}{C}{T}"
    # We use shake_256 as an extendable output function to make sure the hash output has the same bit length as the group order
    k = shake_256(string_to_hash.encode()).digest(int(G1.order()).bit_length())
    k = int.from_bytes(k, "big") % G1.order()

    s0 = (k * t + t0) % G1.order()
    for elem in ts:
        ts[elem] = (k * attributes[elem] + ts[elem]) % G1.order()

    return CommitmentProof(T, k, s0, ts)


def verify_nizkp(
        basis: Tuple[GElement, List[GElement]],
        C: GElement,
        pi: CommitmentProof
    ) -> bool:
    """ Verify non-interactive zero-knowledge proof """
    prod = basis[0] ** pi.s0
    for attr_key, attr_val in pi.ts.items():
        prod *= basis[1][attr_key] ** attr_val

    return prod == C ** pi.k * pi.T

######################
## SIGNATURE SCHEME ##
######################

def generate_key(
        attributes: List[Attribute]
    ) -> Tuple[PublicKey, SecretKey]:
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

    return PublicKey(g, Y, g_tilde, X_tilde, Y_tilde), SecretKey(x, X, y)


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
    ) -> Tuple[IssueRequest, int]:
    """ Create an issuance request

    This corresponds to the "user commitment" step in the issuance protocol.

    *Warning:* You may need to pass state to the `obtain_credential` function.
    """
    t = G1.order().random()
    C = pk.g ** t
    for attr_key, attr_val in user_attributes.items():
        C *= pk.Y[attr_key] ** attr_val

    # ZKP
    basis = (
        pk.g,
        pk.Y
    )
    pi = nizkp(basis, C, t, user_attributes)

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
    assert verify_nizkp((pk.g, pk.Y), request.C, request.pi), "User commitment correct computation zero-knowledge proof verification failed."

    # Sign
    # This part could be "simplified" to the following if we overlook the difference
    # between picking a random u \in \mathbb{Z}_p and then assigning left = g ** u, (ABC scheme)
    # and picking a random generator h \in G_1 (signature scheme)
    """
    # Make sure we account for the user_attributes because their y's are in sk too
    signature = sign(sk, [issuer_attributes[i] if i in issuer_attributes else 0 for i in range(L)])
    signature = (signature[0], signature[1] * request.C)
    """
    # For now we just compute it explicitly
    u = G1.order().random()

    left = pk.g ** u

    right = sk.X * request.C
    for attribute in issuer_attributes:
        right *= pk.Y[attribute] ** issuer_attributes[attribute]

    right **= u

    # Not necessary to return issuer_attributes here, the application will handle this being sent to the user
    # return (left, right), issuer_attributes
    return (left, right)


def obtain_credential( 
        pk: PublicKey,
        response: BlindSignature,
        t: int,
        attributes: AttributeMap
    ) -> AnonymousCredential:
    """ Derive a credential from the issuer's response

    This corresponds to the "Unblinding signature" step.
    """
    # return (response[0], response[1] * (response[0].inverse() ** t))
    return ((response[0], response[1] // (response[0] ** t)), attributes)


## SHOWING PROTOCOL ##

def create_disclosure_proof(
        pk: PublicKey,
        credential: AnonymousCredential,
        hidden_attributes: List[Attribute] #,
        # message: bytes
    ) -> DisclosureProof:
    """ Create a disclosure proof """
    L = len(pk.Y)

    r, t = G1.order().random(), G1.order().random()

    sigma = credential[0]
    attributes = credential[1]

    hidden_attributes = set(hidden_attributes) # for efficiency
    disclosed_attributes = {k: v for k, v in attributes.items() if k not in hidden_attributes}
    hidden_attributes = {k: v for k, v in attributes.items() if k in hidden_attributes}

    sigma_prime: Signature = (sigma[0] ** r, (sigma[1] * sigma[0] ** t) ** r)

    # ZKP
    # First we compute the commitment
    C = sigma_prime[1].pair(pk.g_tilde)
    for attr_key, attr_val in disclosed_attributes.items():
        C *= sigma_prime[0].pair(pk.Y_tilde[attr_key]) ** -attr_val
    
    C //= sigma_prime[0].pair(pk.X_tilde)

    # Compute zkp
    basis = (
        sigma_prime[0].pair(pk.g_tilde),
        [sigma_prime[0].pair(pk.Y_tilde[i]) for i in range(L)]
    )
    pi = nizkp(basis, C, t, hidden_attributes)

    return DisclosureProof(sigma_prime, disclosed_attributes, pi)


def verify_disclosure_proof(
        pk: PublicKey,
        disclosure_proof: DisclosureProof #,
        # message: bytes
    ) -> bool:
    """ Verify the disclosure proof

    Hint: The verifier may also want to retrieve the disclosed attributes
    """

    if disclosure_proof.signature[0] == G1.neutral_element():
        return False

    L = len(pk.Y)

    # Verify request ZKP
    # recompute commitment
    C = disclosure_proof.signature[1].pair(pk.g_tilde)
    for attr_key, attr_val in disclosure_proof.disclosed_attributes.items():
        C *= disclosure_proof.signature[0].pair(pk.Y_tilde[attr_key]) ** -attr_val
    
    C //= disclosure_proof.signature[0].pair(pk.X_tilde)

    basis = (
        disclosure_proof.signature[0].pair(pk.g_tilde),
        [disclosure_proof.signature[0].pair(pk.Y_tilde[i]) for i in range(L)]
    )

    return verify_nizkp(basis, C, disclosure_proof.pi)
