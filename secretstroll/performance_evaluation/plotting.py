import numpy as np
import matplotlib.pyplot as plt
import json

# Data
filename = "evaluation_keygen_data.txt"

with open(filename, "rt") as f:
    contents = '{'
    contents += f.read()[:-2]
    contents += '}'

data = json.loads(contents)
data = {int(key): val for key, val in data.items()}

x = sorted(data)
means = [np.mean(data[k]) for k in x]
sems = [np.std(data[k], ddof=1) / np.sqrt(len(data[k])) for k in x]

fig, ax = plt.subplots(figsize=(5,5))
ax.errorbar(
    x, means, yerr=sems,
    marker='o', linestyle='-',
    capsize=5, elinewidth=2, markeredgewidth=1.5
)

ax.set_xlabel('Number of attributes')
ax.set_ylabel('Mean ± SEM execution time (s)')
# ax.set_title('Execution time of the Key Generation algorithm when varying attribute list size')

# Zoom in on the SEM region
lower = min(means) - 20*max(sems)
upper = max(means) + 20*max(sems)
ax.set_ylim(lower, upper)

ax.grid(True)

fig.savefig('plot_keygen.svg', format='svg', bbox_inches='tight')

plt.show()