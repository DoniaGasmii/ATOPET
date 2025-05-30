import os
import csv
import numpy as np
import pyshark

# === CONFIG ===
TRACE_DIR = "trace_dataset"
OUTPUT_CSV = "traffic_features.csv"
NUM_CELLS = 100
TRIALS_PER_CELL = 100
BATCH_SIZE = 20

def extract_features_from_pcap(pcap_path):
    print(f"[DEBUG] Reading: {pcap_path}")
    try:
        cap = pyshark.FileCapture(pcap_path, use_json=True)
        packets = list(cap)
        cap.close()
    except Exception as e:
        print(f"[ERROR] Failed to open {pcap_path}: {e}")
        return None

    if not packets:
        print(f"[WARN] No packets in {pcap_path}")
        return None

    try:
        times = [float(pkt.sniff_timestamp) for pkt in packets if hasattr(pkt, 'sniff_timestamp')]
        sizes = [int(pkt.length) for pkt in packets if hasattr(pkt, 'length')]
    except Exception as e:
        print(f"[ERROR] Parsing error in {pcap_path}: {e}")
        return None

    if len(times) < 1 or len(sizes) < 1:
        print(f"[WARN] Insufficient data in {pcap_path}")
        return None

    duration = times[-1] - times[0] if len(times) > 1 else 0
    inter_arrival = np.diff(times) if len(times) > 1 else [0]

    features = {
        "total_packets": len(packets),
        "total_bytes": sum(sizes),
        "avg_packet_size": np.mean(sizes),
        "min_packet_size": min(sizes),
        "max_packet_size": max(sizes),
        "duration": duration,
        "mean_inter_arrival": np.mean(inter_arrival),
        "std_inter_arrival": np.std(inter_arrival),
    }
    print(f"[DEBUG] Features extracted for {pcap_path}")
    return features


# === FEATURE EXTRACTION LOOP + INCREMENTAL WRITE ===
print(f"[INFO] Starting extraction... Writing to {OUTPUT_CSV}")
first_write = True

with open(OUTPUT_CSV, mode="w", newline="") as f:
    writer = None

    for start in range(1, TRIALS_PER_CELL + 1, BATCH_SIZE):
        end = min(start + BATCH_SIZE, TRIALS_PER_CELL + 1)
        print(f"\n[INFO] --- Processing batch {start}-{end-1} ---")

        for cell_id in range(1, NUM_CELLS + 1):
            cell_folder = os.path.join(TRACE_DIR, f"cell_{cell_id:03d}")
            print(f"[INFO] Cell: {cell_id} → Folder: {cell_folder}")

            if not os.path.isdir(cell_folder):
                print(f"[WARN] Folder not found: {cell_folder}")
                continue

            for trial_idx in range(start, end):
                fname = f"trace_{trial_idx:03d}.pcap"
                fpath = os.path.join(cell_folder, fname)

                if not os.path.isfile(fpath):
                    print(f"[WARN] File not found: {fpath}")
                    continue

                features = extract_features_from_pcap(fpath)
                if features:
                    features["label"] = cell_id
                    if first_write:
                        writer = csv.DictWriter(f, fieldnames=features.keys())
                        writer.writeheader()
                        first_write = False
                    writer.writerow(features)
                    f.flush()
                    print(f"[INFO] Wrote: {fpath}")
                else:
                    print(f"[WARN] Skipped: {fpath}")

print(f"[DONE] Extraction complete. Saved to {OUTPUT_CSV}")
