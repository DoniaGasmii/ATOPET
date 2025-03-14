"""
Integration tests that verify different aspects of the protocol.
You can *add* new tests here, but it is best to  add them to a new test file.

ALL EXISTING TESTS IN THIS SUITE SHOULD PASS WITHOUT ANY MODIFICATION TO THEM.
"""

import time
from multiprocessing import Process, Queue

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results


def suite(parties, expr, expected):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)

    for result in results:
        assert result == expected


def circuit():
    """
    hashing function with one document provider and 4 third-party SMC participants
    f(a', b, c, d, e) = K - ba' + ca'^2 - da'^3 + ea^4
    # TODO addition and multiplication by constants, and subtraction, more constant than just first K
    (computed over a finite field)
    """
    alice_document, alice_coef = Secret(), Secret()
    bob_coef = Secret()
    charlie_coef = Secret()
    daniel_coef = Secret()
    eva_coef = Secret()

    parties = {
        "Alice": {alice_document: 146123893, alice_coef: 93943},
        "Bob": {bob_coef: 1234},
        "Charlie": {charlie_coef: 42346},
        "Daniel": {daniel_coef: 462},
        "Eva": {eva_coef: 752},
    }

    expr = (alice_coef + alice_coef * (bob_coef + alice_coef * (charlie_coef + alice_coef * (daniel_coef + alice_coef * eva_coef))))
    expected = ...
    suite(parties, expr, expected)