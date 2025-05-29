import numpy as np
# import matplotlib.pyplot as plt
import json

def plot_keygen():
    filename = "evaluation_keygen_data.txt"

    with open(filename, "rt") as f:
        contents = '{' + f.read()[:-2] + '}'

    data = json.loads(contents)
    data = {int(key): val for key, val in data.items()}

    x = sorted(data)
    means = [np.mean(data[k]) for k in x]
    sems = [np.std(data[k], ddof=1) / np.sqrt(len(data[k])) for k in x]

    for i in range(len(means)):
        print(f"${means[i]*10**3:.2f} \\pm {sems[i]*10**3:.3f}$ & ", end="")

    # fig, ax = plt.subplots(figsize=(5,5))
    # ax.errorbar(
    #     x, means, yerr=sems,
    #     marker='o', linestyle='-',
    #     capsize=5, elinewidth=2, markeredgewidth=1.5
    # )

    # ax.set_xlabel('Number of attributes')
    # ax.set_ylabel('Mean ± SEM execution time (s)')
    # ax.set_title('Execution time of the Key Generation algorithm when varying attribute list size')

    # Zoom in on the SEM region
    # lower = min(means) - 20*max(sems)
    # upper = max(means) + 20*max(sems)
    # ax.set_ylim(lower, upper)
    # ax.grid(True)
    # fig.savefig('plot_keygen.svg', format='svg', bbox_inches='tight')
    # plt.show()

def plot_keyret():
    filename = "evaluation_keyret_data.txt"

    with open(filename, "rt") as f:
        contents = f.read()

    data = json.loads(contents)
    data = {int(key): val for key, val in data.items()}

    x = sorted(data)
    means = [np.mean(data[k]) for k in x]
    # sems = [np.std(data[k], ddof=1) / np.sqrt(len(data[k])) for k in x]

    # fig, ax = plt.subplots(figsize=(5,5))
    # ax.errorbar(
    #     x, means, # yerr=sems,
    #     marker='o', linestyle='-',
    #     capsize=5, elinewidth=2, markeredgewidth=1.5
    # )

    # ax.set_xlabel('Number of attributes')
    # ax.set_ylabel('Communication cost (bytes)')
    # # ax.set_title('Execution time of the Key Generation algorithm when varying attribute list size')

    # # Zoom in on the SEM region
    # lower = min(means) - 2000 # - 20*max(sems)
    # upper = max(means) + 2000 # + 20*max(sems)
    # ax.set_ylim(lower, upper)

    # ax.grid(True)

    # fig.savefig('plot_keyret.svg', format='svg', bbox_inches='tight')

    # plt.show()


def process_issuance():
    filename = "evaluation_issuance_data.txt"

    with open(filename, "rt") as f:
        contents = '{' + f.read()[:-2] + '}'

    data = json.loads(contents)
    data = {int(key): val for key, val in data.items()}

    x = sorted(data)
    means = [np.mean(data[k]) for k in x]
    sems = [np.std(data[k], ddof=1) / np.sqrt(len(data[k])) for k in x]

    for i in range(len(means)):
        print(f"${means[i]*10**3:.2f} \\pm {sems[i]*10**3:.3f}$ & ", end="")


def process_showing():
    filename = "evaluation_showing_data.txt"

    with open(filename, "rt") as f:
        contents = '{' + f.read()[:-2] + '}'

    data = json.loads(contents)
    data = {int(key): val for key, val in data.items()}

    x = sorted(data)
    means = [np.mean(data[k]) for k in x]
    sems = [np.std(data[k], ddof=1) / np.sqrt(len(data[k])) for k in x]

    for i in range(len(means)):
        print(f"${means[i]*10**3:.2f} \\pm {sems[i]*10**3:.3f}$ & ", end="")

    
def process_verification():
    filename = "evaluation_verification_data.txt"

    with open(filename, "rt") as f:
        contents = '{' + f.read()[:-2] + '}'

    data = json.loads(contents)
    data = {int(key): val for key, val in data.items()}

    x = sorted(data)
    means = [np.mean(data[k]) for k in x]
    sems = [np.std(data[k], ddof=1) / np.sqrt(len(data[k])) for k in x]

    for i in range(len(means)):
        print(f"${means[i]*10**3:.2f} \\pm {sems[i]*10**3:.3f}$ & ", end="")


import matplotlib.pyplot as plt

# New data
data = {
    "4": 10512,
    "10": 10008,
    "20": 9178,
    "40": 7518,
    "60": 5858,
    "100": 2538
}

x = list(map(int, data.keys()))
y = [data[str(k)] for k in x]

fig, ax = plt.subplots(figsize=(5, 5))

ax.plot(x, y, marker='o', linestyle='-')
ax.set_xlabel('Attributes disclosed')
ax.set_ylabel('Communication cost (bytes)')
ax.grid(True)

fig.savefig('plot_extra.svg', format='svg', bbox_inches='tight')

plt.show()

