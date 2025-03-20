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


def test_circuit():
    """
    Multiple medical providers contribute different pieces of a patient's health data as a score.
    A circuit gets this data as input and computes the final disease risk score.
    In this circuit, we have:
    The patient's age is a public constant K = 50 known by all parties.
    Doctor A is a cardiologist and provides the Blood Pressure score.
    Doctor B is a pulmonologist and provides the Smoking History score.
    Doctor C is an endocrinologist and provides the Diabetes score.
    Doctor D is the patient's family doctor and provides the patient's Healthy Lifestyle score.

    The disease risk score c is defined by the following formula (values chosen arbitrarily):
    c = 5 x A + 2 x B x C - D + K
    (computed over a finite field)
    """

    doca_secret, docb_secret, docc_secret, docd_secret = Secret(), Secret(), Secret(), Secret()

    parties = {
        "DocA": {doca_secret: 30},
        "DocB": {docb_secret: 100},
        "DocC": {docc_secret: 10},
        "DocD": {docd_secret: 2},
    }
    expr = ((Scalar(5) * doca_secret) + (docb_secret * docc_secret) - docd_secret + Scalar(50))
    expected = (5 * 30) + (100 * 10) - 2 + 50
    suite(parties, expr, expected)