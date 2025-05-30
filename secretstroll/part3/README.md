# Part 3 - Cell Fingerprinting via Network Traffic Analysis

This folder contains the full implementation of Part 3 of the project: a network traffic analysis attack to infer the cell ID queried by a user of the SecretStroll app.

## Files in this repository
This folder contains the full implementation of Part 3:

- `client.py` / `server.py` / `stroll.py` / `credential.py` / `serialization.py` — Core SecretStroll components.
- `docker-compose.yaml` — Launches client and server containers with Tor routing.
- `fingerprint.db` — Database of POIs used by the server.
- `collect_traces.sh` — Automated script to collect packet traces for fingerprinting.
- `fingerprinting.py` — Random Forest classifier training and evaluation pipeline.
- `traffic_analysis/`:
    - `extract_features.py` — Extracts traffic features from `.pcap` traces.
    - `traffic_features_analysis.ipynb` — Optional notebook for visualization.
    - `trace_dataset/` (generated) — Collected `.pcap` traffic traces (created by `collect_traces.sh`).
    - `traffic_features.csv` (generated) — Extracted features for training.

## How to Run Trace Collection
Start fresh
bash
`
cd sf_secretstroll
chmod 777 tor         
docker compose down
docker compose build
docker compose up -d
`
Terminal 1: Start server
`
docker exec -it cs523-server /bin/bash
cd /server
python3 server.py setup -p key.pub -s key.sec -S restaurant -S bar -S dojo
python3 server.py run -p key.pub -s key.sec -D fingerprint.db
`
Terminal 2: Start client + run trace collection
`
docker exec -it cs523-client /bin/bash
cd /client
python3 client.py get-pk
python3 client.py register -u student -S restaurant -S bar -S dojo
python3 client.py grid 42 -T restaurant    # (optional test query)
`
# Now run trace collection:
`
bash collect_traces.sh
`
Check results
ls /traffic_analysis/trace_dataset
✅ The .pcap trace files should appear here.


    
