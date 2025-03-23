import os
import sys
import csv
import statistics

# Add helper_functions directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helper_functions')))

from evaluation_helper_functions import run_multiplication_experiment

# ===============================
# Experiment: Effect of number of multiplications
# ===============================

# Parameters for the experiment
num_parties = 5  # Fixed number of participants
multiplication_counts = [10, 30, 70, 100]  # Varying number of multiplication operations
repeat_runs = 5  # Repetitions for statistical accuracy

# Directory to store experiment logs
log_dir = "../performance_evaluation_logs"
os.makedirs(log_dir, exist_ok=True)

# Path to the CSV log file for this experiment
log_file = os.path.join(log_dir, "effect_num_multiplications.csv")

# Initialize the CSV with header if it doesn't exist
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["num_operations", "mean_computation_time", "std_computation_time",
                         "mean_communication_cost", "std_communication_cost"])

# Run experiments for each value of number of multiplications
for num_ops in multiplication_counts:
    computation_times = []
    communication_costs = []

    for _ in range(repeat_runs):
        computation_cost, communication_cost = run_multiplication_experiment(num_parties, num_ops)
        computation_times.append(computation_cost)
        communication_costs.append(communication_cost)

    # Compute statistics
    mean_comp = statistics.mean(computation_times)
    std_comp = statistics.stdev(computation_times)
    mean_comm = statistics.mean(communication_costs)
    std_comm = statistics.stdev(communication_costs)

    # Append to CSV
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([num_ops, mean_comp, std_comp, mean_comm, std_comm])

print("Multiplication experiment complete. Results saved to:", log_file)
