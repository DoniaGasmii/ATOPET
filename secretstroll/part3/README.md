# Part 3 - Cell Fingerprinting via Network Traffic Analysis

This folder contains the full implementation of Part 3 of the project: a network traffic analysis attack to infer the cell ID queried by a user of the SecretStroll app.

## Structure

- `client.py` / `server.py` / `stroll.py` / `credential.py` / `serialization.py`: Core SecretStroll components.
- `docker-compose.yaml`: Launches client and server containers with Tor routing.
- `fingerprint.db`: Database of POIs used by the server (required).
- `collect_traffic_traces.sh`: Automated script to collect packet traces for fingerprinting.
- `fingerprinting.py`: Random Forest classifier training and evaluation pipeline.
- `traffic_analysis/`:
    - `extract_features.py`: Extracts traffic features from `.pcap` traces.
    - `traffic_features_analysis.ipynb`: Optional notebook for visualizing
