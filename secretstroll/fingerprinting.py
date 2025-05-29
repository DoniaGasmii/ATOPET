import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

CSV_PATH = "traffic_analysis/traffic_features.csv"
LOW_ACCURACY_THRESHOLD = 0.4
PLOTS_DIR = "traffic_analysis/plots"


def classify(train_features, train_labels, test_features, test_labels):
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(train_features, train_labels)
    predictions = clf.predict(test_features)
    return predictions, clf


def perform_crossval(features, labels, folds=10):
    print(f"[INFO] Starting {folds}-fold cross-validation...")
    kf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    all_preds = []
    all_true = []
    fold_accuracies = []
    feature_importance_sum = np.zeros(features.shape[1])

    for fold, (train_idx, test_idx) in enumerate(kf.split(features, labels)):
        print(f"\n[INFO] Fold {fold+1}:")
        X_train, X_test = features[train_idx], features[test_idx]
        y_train, y_test = labels[train_idx], labels[test_idx]
        print(f"  - Train size: {len(y_train)} | Test size: {len(y_test)}")
        preds, clf = classify(X_train, y_train, X_test, y_test)
        fold_acc = accuracy_score(y_test, preds)
        print(f"  - Accuracy: {fold_acc:.4f}")
        fold_accuracies.append(fold_acc)

        all_preds.extend(preds)
        all_true.extend(y_test)
        feature_importance_sum += clf.feature_importances_

    print("\n=== Fold Accuracies ===")
    for i, acc in enumerate(fold_accuracies):
        print(f"  Fold {i+1}: {acc:.4f}")
    print(f"  Mean Accuracy: {np.mean(fold_accuracies):.4f}")

    print("\n=== Overall Evaluation ===")
    report = classification_report(all_true, all_preds, output_dict=True)
    print("F1 Score (weighted):", round(report["weighted avg"]["f1-score"], 4))
    print("Precision (weighted):", round(report["weighted avg"]["precision"], 4))
    print("Recall (weighted):", round(report["weighted avg"]["recall"], 4))

    labels_array = np.array(all_true)
    preds_array = np.array(all_preds)
    unique_labels = np.unique(labels_array)
    label_accuracy = {}

    for label in unique_labels:
        indices = np.where(labels_array == label)[0]
        acc = np.mean(preds_array[indices] == label)
        label_accuracy[label] = acc

    # === Per-Class Accuracy Distribution
    # Plot distribution of accuracies
    accuracies = list(label_accuracy.values())

    os.makedirs("traffic_analysis/plots", exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.hist(accuracies, bins=20, color="skyblue", edgecolor="black")
    plt.xlabel("Accuracy")
    plt.ylabel("Number of Classes")
    plt.tight_layout()
    plt.savefig("traffic_analysis/plots/accuracy_distribution_per_class.png")

    # === Confusion Matrix for Bottom 4 and Top 4 Classes ===
    sorted_labels = sorted(label_accuracy.items(), key=lambda x: x[1])
    bottom_4 = [label for label, _ in sorted_labels[:4]]
    top_4 = [label for label, _ in sorted_labels[-4:]]

    cm_full = confusion_matrix(all_true, all_preds, labels=unique_labels)

    def plot_conf_matrix(selected_labels, name):
        indices = [np.where(unique_labels == lbl)[0][0] for lbl in selected_labels]
        cm = cm_full[np.ix_(indices, indices)]
        label_names = [str(lbl) for lbl in selected_labels]

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=label_names, yticklabels=label_names)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()
        filepath = f"{PLOTS_DIR}/confusion_matrix_{name.lower()}_accuracy_cells.png"
        plt.savefig(filepath)
        print(f"Saved confusion matrix plot to {filepath}")

    os.makedirs(PLOTS_DIR, exist_ok=True)
    plot_conf_matrix(bottom_4, "Lowest")
    plot_conf_matrix(top_4, "Highest")


def load_data():
    print(f"[INFO] Loading data from {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"[INFO] Loaded {len(df)} samples with {len(df.columns)-1} features.")

    labels = df["label"].values
    features = df.drop(columns=["label"]).values
    return features, labels


def main():
    features, labels = load_data()
    perform_crossval(features, labels, folds=10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
