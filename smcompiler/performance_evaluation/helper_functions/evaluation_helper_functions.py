import time
import sys
import csv
import os
import statistics
from multiprocessing import Process, Queue

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from expression import Secret, Scalar 
from protocol import ProtocolSpec
from server import run
from smc_party import SMCParty


# ===============================
# Helper functions
# ===============================

def smc_client(client_id, protocol, value_dict, queue):
    start_time = time.time()
    cli = SMCParty(client_id, "localhost", 5000, protocol_spec=protocol, value_dict=value_dict)
    result = cli.run()
    elapsed = time.time() - start_time
    # Collect communication cost from the client after execution
    comm_cost = cli.comm.bytes_sent + cli.comm.bytes_received
    queue.put({"client_id": client_id, "elapsed_time": elapsed, "comm_cost": comm_cost, "result": result})

def smc_server(args):
    run("localhost", 5000, args)

def run_smc(participants, expr):
    protocol = ProtocolSpec(expr=expr, participant_ids=list(participants.keys()))
    queue = Queue()

    server = Process(target=smc_server, args=(participants,))

    clients = [
        Process(target=smc_client, args=(name, protocol, values, queue))
        for name, values in participants.items()
    ]
    
    global_start = time.time()
    server.start()
    time.sleep(2)
    for client in clients:
        client.start()

    for client in clients:
        client.join()

    server.terminate()
    server.join()
    
    global_elapsed = time.time() - global_start

    results = []
    while not queue.empty():
        results.append(queue.get())

    total_comm = sum(r['comm_cost'] for r in results)
    return global_elapsed, total_comm


# ===============================
# Expression Generators
# ===============================

def generate_add_expr(secret_vars):
    """Creates an expression that adds all secret variables."""
    expr = secret_vars[0]
    for var in secret_vars[1:]:
        expr = expr + var
    return expr

def generate_mul_expr(secret_vars):
    """Creates an expression that multiplies all secret variables."""
    expr = secret_vars[0]
    for var in secret_vars[1:]:
        expr = expr * var
    return expr

def generate_scalar_add_expr(secret_vars):
    """Creates an expression that adds a scalar value (e.g., 5) to each secret variable."""
    expr = secret_vars[0] + Scalar(5)
    for var in secret_vars[1:]:
        expr = expr + (var + Scalar(5))
    return expr

def generate_scalar_mul_expr(secret_vars):
    """Creates an expression that multiplies each secret variable by a scalar value (e.g., 3)."""
    expr = secret_vars[0] * Scalar(3)
    for var in secret_vars[1:]:
        expr = expr * (var * Scalar(3))
    return expr


# ===============================
# Experiment Runners (no logging inside)
# ===============================

def run_addition_experiment(num_parties, num_ops):
    """Evaluate the cost of addition expressions with varying number of parties or operations."""
    secrets = [Secret() for _ in range(num_ops)]
    expr = generate_add_expr(secrets)
    
    party_ids = [f"P{i+1}" for i in range(num_parties)]
    secrets_per_party = num_ops // num_parties
    remaining = num_ops % num_parties
    participants = {}
    i = 0
    for pid in party_ids:
        count = secrets_per_party + (1 if remaining > 0 else 0)
        values = {secrets[j]: 1 for j in range(i, i + count)}
        participants[pid] = values
        i += count
        remaining -= 1

    return run_smc(participants, expr)

def run_multiplication_experiment(num_parties, num_ops):
    """Evaluate the cost of multiplication expressions with varying number of parties or operations."""
    secrets = [Secret() for _ in range(num_ops)]
    expr = generate_mul_expr(secrets)

    party_ids = [f"P{i+1}" for i in range(num_parties)]
    secrets_per_party = num_ops // num_parties
    remaining = num_ops % num_parties
    participants = {}
    i = 0
    for pid in party_ids:
        count = secrets_per_party + (1 if remaining > 0 else 0)
        values = {secrets[j]: 2 for j in range(i, i + count)}
        participants[pid] = values
        i += count
        remaining -= 1
    return run_smc(participants, expr)

def run_scalar_addition_experiment(num_parties, num_ops):
    """Evaluate the cost of scalar additions with varying number of parties or operations."""
    secrets = [Secret() for _ in range(num_ops)]
    expr = generate_scalar_add_expr(secrets)

    party_ids = [f"P{i+1}" for i in range(num_parties)]
    secrets_per_party = num_ops // num_parties
    remaining = num_ops % num_parties
    participants = {}
    i = 0
    for pid in party_ids:
        count = secrets_per_party + (1 if remaining > 0 else 0)
        values = {secrets[j]: 1 for j in range(i, i + count)}
        participants[pid] = values
        i += count
        remaining -= 1
    return run_smc(participants, expr)

def run_scalar_multiplication_experiment(num_parties, num_ops):
    """Evaluate the cost of scalar multiplications with varying number of parties or operations."""
    secrets = [Secret() for _ in range(num_ops)]
    expr = generate_scalar_mul_expr(secrets)

    party_ids = [f"P{i+1}" for i in range(num_parties)]
    secrets_per_party = num_ops // num_parties
    remaining = num_ops % num_parties
    participants = {}
    i = 0
    for pid in party_ids:
        count = secrets_per_party + (1 if remaining > 0 else 0)
        values = {secrets[j]: 2 for j in range(i, i + count)}
        participants[pid] = values
        i += count
        remaining -= 1

    return run_smc(participants, expr)
