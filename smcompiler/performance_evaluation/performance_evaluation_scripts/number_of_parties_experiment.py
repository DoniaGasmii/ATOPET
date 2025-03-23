import os
import sys
import csv
import statistics
import time

# Add helper_functions to the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helper_functions')))
from evaluation_helper_functions import run_addition_experiment

# ===============================
# Experiment: Effect of number of parties
# ===============================

# Parameters for the experiment
fixed_num_operations = 50  # Fixed number of addition operations
party_counts = [3, 5, 7, 10, 20, 40]  # Varying number of parties
repeat_runs = 5  # Number of repetitions per setting

# Directory to store results
log_dir = "../performance_evaluation_logs"
os.makedirs(log_dir, exist_ok=True)

# Path to CSV log file
log_file = os.path.join(log_dir, "effect_num_parties.csv")

# Create CSV file with header if not present
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "num_parties",
            "mean_computation_time", "std_computation_time",
            "mean_communication_cost", "std_communication_cost"
        ])

# Run experiment for each number of parties
for num_parties in party_counts:
    computation_times = []
    communication_costs = []

    for _ in range(repeat_runs):
        try:
            computation_cost, communication_cost = run_addition_experiment(num_parties, fixed_num_operations)
            computation_times.append(computation_cost)
            communication_costs.append(communication_cost)
        except Exception as e:
            print(f"⚠️ Experiment failed for {num_parties} parties: {e}")


    mean_comp = statistics.mean(computation_times)
    std_comp = statistics.stdev(computation_times)
    mean_comm = statistics.mean(communication_costs)
    std_comm = statistics.stdev(communication_costs)

    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([num_parties, mean_comp, std_comp, mean_comm, std_comm])

print("Number of Parties experiment complete. Results saved to:", log_file)
