"""
Classes that you need to complete.
"""

from typing import Any, Dict, List, Union, Tuple

from credential import (generate_key,
                        create_issue_request, sign_issue_request, obtain_credential,
                        create_disclosure_proof, verify_disclosure_proof)

# Optional import
from serialization import jsonpickle

# Type aliases
State = Any


def serialize(
        obj: Any
    ) -> bytes:
    return jsonpickle.encode(obj).encode()


def deserialize(
        data: bytes
    ) -> Any:
    return jsonpickle.decode(data.decode())


class Server:
    """Server"""


    def __init__(self):
        """
        Server constructor.
        """
        ###############################################
        # TODO: Complete this function.
        ###############################################
        # raise NotImplementedError
        pass


    @staticmethod
    def generate_ca(
            subscriptions: List[str]
        ) -> Tuple[bytes, bytes]:
        """Initializes the credential system. Runs exactly once in the
        beginning. Decides on schemes public parameters and choses a secret key
        for the server.

        Args:
            subscriptions: a list of all valid attributes. Users cannot get a
                credential with a attribute which is not included here.

        Returns:
            tuple containing:
                - server's secret key
                - server's public information
            You are free to design this as you see fit, but the return types
            should be encoded as bytes.
        """
        subscriptions.append("user_secret_key")
        sk, pk = generate_key(subscriptions)

        return serialize(sk), serialize(pk)


    def process_registration(
            self,
            server_sk: bytes,
            server_pk: bytes,
            issuance_request: bytes,
            username: str,
            subscriptions: List[str]
        ) -> bytes:
        """ Registers a new account on the server.

        Args:
            server_sk: the server's secret key (serialized)
            server_pk: the server's public key (serialized)
            issuance_request: The issuance request (serialized)
            username: username
            subscriptions: attributes


        Return:
            serialized response (the client should be able to build a
                credential with this response).
        """
        server_sk = deserialize(server_sk)
        server_pk = deserialize(server_pk)
        issuance_request = deserialize(issuance_request)

        issuer_attributes = {
            "username": int.from_bytes(username.encode(), "big")
        }
        issuer_attributes.update(dict(zip(subscriptions, [1 for _ in range(len(subscriptions))])))

        blind_signature = sign_issue_request(server_sk, server_pk, issuance_request, issuer_attributes)
        response = (blind_signature, issuer_attributes)

        return serialize(response)


    def check_request_signature(
        self,
        server_pk: bytes,
        message: bytes,
        revealed_attributes: List[str],
        signature: bytes
        ) -> bool:
        """ Verify the signature on the location request

        Args:
            server_pk: the server's public key (serialized)
            message: The message to sign
            revealed_attributes: revealed attributes
            signature: user's authorization (serialized)

        Returns:
            whether a signature is valid
        """
        server_pk = deserialize(server_pk)
        disclosure_proof = deserialize(signature)

        # On top of checking the validity of the signature, we also have to check
        # that the user is indeed subscribed to all the requested types
        for attribute in revealed_attributes:
            if attribute not in disclosure_proof or disclosure_proof[1][attribute] != 1:
                return False

        result = verify_disclosure_proof(server_pk, disclosure_proof, message)
        return result


class Client:
    """Client"""

    def __init__(self):
        """
        Client constructor.
        """
        ###############################################
        # TODO: Complete this function.
        ###############################################
        # raise NotImplementedError()
        pass


    def prepare_registration(
            self,
            server_pk: bytes,
            username: str,
            subscriptions: List[str]
        ) -> Tuple[bytes, State]:
        """Prepare a request to register a new account on the server.

        Args:
            server_pk: a server's public key (serialized)
            username: user's name
            subscriptions: user's subscriptions

        Return:
            A tuple containing:
                - an issuance request
                - A private state. You can use state to store and transfer information
                from prepare_registration to proceed_registration_response.
                You need to design the state yourself.
        """
        server_pk = deserialize(server_pk)


        # We're choosing option 1, so username is an issuer attribute
        # user_attributes = {
        #     "username": username,
        # }
        user_attributes = {
            "user_secret_key": 1234 # TODO: check utility of this?
        }

        issuance_request, t = create_issue_request(server_pk, user_attributes)

        return serialize(issuance_request), (user_attributes, t)


    def process_registration_response(
            self,
            server_pk: bytes,
            server_response: bytes,
            private_state: State
        ) -> bytes:
        """Process the response from the server.

        Args:
            server_pk a server's public key (serialized)
            server_response: the response from the server (serialized)
            private_state: state from the prepare_registration
            request corresponding to this response

        Return:
            credentials: create an attribute-based credential for the user
        """
        server_pk = deserialize(server_pk)
        response = deserialize(server_response)

        blind_signature = response[0]
        issuer_attributes = response[1]

        user_attributes = private_state[0]
        t = private_state[1]

        attributes = user_attributes | issuer_attributes

        credential = obtain_credential(server_pk, blind_signature, t, attributes)

        return serialize(credential)


    def sign_request(
            self,
            server_pk: bytes,
            credentials: bytes,
            message: bytes,
            types: List[str]
        ) -> bytes:
        """Signs the request with the client's credential.

        Arg:
            server_pk: a server's public key (serialized)
            credential: client's credential (serialized)
            message: message to sign
            types: which attributes should be sent along with the request?

        Returns:
            A message's signature (serialized)
        """
        server_pk = deserialize(server_pk)
        credential = deserialize(credentials)

        attributes = credential[1]
        types = set(types)
        hidden_attributes = [attribute for attribute in attributes if attribute not in types]

        disclosure_proof = create_disclosure_proof(server_pk, credential, hidden_attributes, message)

        return serialize(disclosure_proof)
