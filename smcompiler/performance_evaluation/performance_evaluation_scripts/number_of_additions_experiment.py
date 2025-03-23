import os
import sys
import csv
import statistics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helper_functions')))

from evaluation_helper_functions import run_addition_experiment

# ===============================
# Experiment: Effect of number of additions
# ===============================

# Parameters for the experiment
num_parties = 5  # Fixed number of participants
addition_counts = [10, 30, 70, 100]  # Varying number of addition operations
repeat_runs = 5  # Number of times each experiment is repeated to compute mean and std

# Directory to store the experiment results
log_dir = "../performance_evaluation_logs"
os.makedirs(log_dir, exist_ok=True)

# Path to the CSV log file for this experiment
log_file = os.path.join(log_dir, "effect_num_additions.csv")

# Initialize the CSV file with header if it doesn't exist
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["num_operations", "mean_computation_time", "std_computation_time",
                         "mean_communication_cost", "std_communication_cost"])

# Run the experiments
for num_ops in addition_counts:
    computation_times = []
    communication_costs = []

    # Repeat the experiment multiple times for statistical reliability
    for _ in range(repeat_runs):
        computation_cost, communication_cost = run_addition_experiment(num_parties, num_ops)
        computation_times.append(computation_cost)
        communication_costs.append(communication_cost)

    # Compute mean and standard deviation for both metrics
    mean_comp = statistics.mean(computation_times)
    std_comp = statistics.stdev(computation_times)
    mean_comm = statistics.mean(communication_costs)
    std_comm = statistics.stdev(communication_costs)

    # Log results to CSV
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([num_ops, mean_comp, std_comp, mean_comm, std_comm])

print("Addition experiment complete. Results saved to:", log_file)
