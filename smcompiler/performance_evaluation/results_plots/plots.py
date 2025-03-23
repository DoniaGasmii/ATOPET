import subprocess
subprocess.call(["pip", "install", "pandas"])
subprocess.call(["pip", "install", "matplotlib"])

import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_experiment_results(csv_path, metric, ylabel, title, output_name):
    """
    Plot mean ± std error bars for a metric (computation or communication) using pandas.

    Args:
        csv_path (str): Path to the CSV log file.
        metric (str): Either "computation" or "communication".
        ylabel (str): Label for the y-axis.
        title (str): Plot title.
        output_name (str): Filename to save the plot (without extension).
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Select appropriate columns based on the metric
    if metric == "computation":
        y = df["mean_computation_time"]
        yerr = df["std_computation_time"]
    elif metric == "communication":
        y = df["mean_communication_cost"]
        yerr = df["std_communication_cost"]
    else:
        raise ValueError("Metric must be either 'computation' or 'communication'.")

    x = df["num_operations"] if "num_operations" in df.columns else df["num_parties"]

    # Plotting
    plt.figure()
    plt.errorbar(x, y, yerr=yerr, fmt='o-', capsize=5, linewidth=2)
    plt.xlabel("Number of Operations" if "num_operations" in df.columns else "Number of Parties")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)

    # Save plot
    plt.savefig(os.path.join(f"{output_name}.png"))
    plt.close()

# =========================
# Usage for Additions
# =========================
plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_additions.csv",
    metric="computation",
    ylabel="Computation Cost (s)",
    title="Computation Cost vs Number of Additions",
    output_name="addition_computation_cost"
)

plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_additions.csv",
    metric="communication",
    ylabel="Communication Cost (bytes)",
    title="Communication Cost vs Number of Additions",
    output_name="addition_communication_cost"
)

# =========================
# Usage for Multiplications
# =========================
plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_multiplications.csv",
    metric="computation",
    ylabel="Computation Cost (s)",
    title="Computation Cost vs Number of Multiplications",
    output_name="multiplication_computation_cost"
)

plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_multiplications.csv",
    metric="communication",
    ylabel="Communication Cost (bytes)",
    title="Communication Cost vs Number of Multiplications",
    output_name="multiplication_communication_cost"
)

# =========================
# Usage for Scalar Additions
# =========================
plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_scalar_additions.csv",
    metric="computation",
    ylabel="Computation Cost (s)",
    title="Computation Cost vs Number of Scalar Additions",
    output_name="scalar_addition_computation_cost"
)

plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_scalar_additions.csv",
    metric="communication",
    ylabel="Communication Cost (bytes)",
    title="Communication Cost vs Number of Scalar Additions",
    output_name="scalar_addition_communication_cost"
)

# =========================
# Usage for Scalar Multiplications
# =========================
plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_scalar_multiplications.csv",
    metric="computation",
    ylabel="Computation Cost (s)",
    title="Computation Cost vs Number of Scalar Multiplications",
    output_name="scalar_multiplication_computation_cost"
)

plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_scalar_multiplications.csv",
    metric="communication",
    ylabel="Communication Cost (bytes)",
    title="Communication Cost vs Number of Scalar Multiplications",
    output_name="scalar_multiplication_communication_cost"
)

# =========================
# Usage for Number of Parties
# =========================
plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_parties.csv",
    metric="computation",
    ylabel="Computation Cost (s)",
    title="Computation Cost vs Number of Parties",
    output_name="num_parties_computation_cost"
)

plot_experiment_results(
    csv_path="../performance_evaluation_logs/effect_num_parties.csv",
    metric="communication",
    ylabel="Communication Cost (bytes)",
    title="Communication Cost vs Number of Parties",
    output_name="num_parties_communication_cost"
)
