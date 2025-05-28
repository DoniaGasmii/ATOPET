from credential import (generate_key, sign, verify,
                        create_issue_request, sign_issue_request, obtain_credential,
                        create_disclosure_proof, verify_disclosure_proof)

import time
from os.path import join

dirname = "performance_evaluation"
n = 20
attribute_numbers = [4, 10, 20, 40, 60, 100]

def run(function, n, *args):
    times = []
    for i in range(n):
        start_time = time.time()
        function(*args)
        times.append(time.time() - start_time)

    return times

# 1. Key generation
# We vary the amount of attributes to see how costs scale
def evaluate_key_generation():
    filename = "evaluation_keygen_data.txt"
    with open(join(dirname, filename), "at") as f:
        for attribute_number in attribute_numbers:
            attribute_list = [i for i in range(attribute_number)]

            times = run(generate_key, n, attribute_list)

            f.write(f'"{attribute_number}": {times}, ')

# 2. Credential issuance
def issuance(attribute_number, sk, pk):
    user_attributes = {
        "private_key": 1234
    }
    request, t = create_issue_request(pk, user_attributes)

    issuer_attributes = {str(i): 0 for i in range(attribute_number - 1)} # negligible cost
    blind_signature = sign_issue_request(sk, pk, request, issuer_attributes)

    attributes = user_attributes | issuer_attributes
    credential = obtain_credential(pk, blind_signature, t, attributes)

    return credential

def evaluate_issuance():
    filename = "evaluation_issuance_data.txt"
    with open(join(dirname, filename), "at") as f:
        for attribute_number in attribute_numbers:
            attribute_list = ["private_key"] + [str(i) for i in range(attribute_number - 1)]

            sk, pk = generate_key(attribute_list)
            times = run(issuance, n, attribute_number, sk, pk)

            f.write(f'"{attribute_number}": {times}, ')

# 3. Credential showing
def evaluate_showing():
    filename = "evaluation_showing_data.txt"
    with open(join(dirname, filename), "at") as f:
        for attribute_number in attribute_numbers:
            attribute_list = ["private_key"] + [str(i) for i in range(attribute_number - 1)]
            sk, pk = generate_key(attribute_list)
            credential = issuance(attribute_number, sk, pk)

            hidden_attributes = ["private_key"]

            message = b"SIGNED MESSAGE"

            times = run(create_disclosure_proof, n, pk, credential, hidden_attributes, message)

            f.write(f'"{attribute_number}": {times}, ')


# 4. Credential verification
def evaluate_verification():
    filename = "evaluation_verification_data.txt"
    with open(join(dirname, filename), "at") as f:
        for attribute_number in attribute_numbers:
            attribute_list = ["private_key"] + [str(i) for i in range(attribute_number - 1)]
            sk, pk = generate_key(attribute_list)
            credential = issuance(attribute_number, sk, pk)

            hidden_attributes = ["private_key"]

            message = b"SIGNED MESSAGE"
            disclosure_proof = create_disclosure_proof(pk, credential, hidden_attributes, message)

            times = run(verify_disclosure_proof, n, pk, disclosure_proof, message)

            f.write(f'"{attribute_number}": {times}, ')

evaluate_verification()