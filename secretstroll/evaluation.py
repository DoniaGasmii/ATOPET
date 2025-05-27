from credential import (generate_key, sign, verify,
                        create_issue_request, sign_issue_request, obtain_credential,
                        create_disclosure_proof, verify_disclosure_proof)

import time
from os.path import join

def run(function, n, *args):
    times = []
    for i in range(n):
        start_time = time.time()
        function(*args)
        times.append(time.time() - start_time)

    return times

dirname = "performance_evaluation"
n = 20

# 1. Key generation
# We vary the amount of attributes to see how costs scale
attribute_numbers = [4, 6, 8, 10, 20, 40, 60, 100]
filename = "evaluation_keygen_data.txt"
with open(join(dirname, filename), "at") as f:
    for attribute_number in attribute_numbers:
        attribute_list = [i for i in range(attribute_number)]

        times = run(generate_key, n, attribute_list)

        f.write(f'"{attribute_number}": {times}, ')