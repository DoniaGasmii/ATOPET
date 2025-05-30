#!/usr/bin/env bash
# collect_traffic_traces.sh
# Author: Donia Gasmi
# Description:
# This script collects network traffic traces for SecretStroll queries
# by capturing packets while querying POIs for each grid cell.

set -euo pipefail

TRACE_DIR=/client/traffic_analysis/trace_dataset
NETWORK_IFACE=eth0
PCAP_FILTER='not port 9050'
NUM_TRIALS=100  # Number of queries per cell

mkdir -p "$TRACE_DIR"

for cell_id in $(seq -w 1 100); do
  CELL_OUTPUT_PATH="$TRACE_DIR/cell_${cell_id}"
  mkdir -p "$CELL_OUTPUT_PATH"
  echo "▶ Collecting traces for cell $cell_id → $CELL_OUTPUT_PATH"

  for trial_idx in $(seq -w 1 $NUM_TRIALS); do
    TRACE_FILENAME="$CELL_OUTPUT_PATH/trace_${trial_idx}.pcap"
    
    # Start packet capture in the background
    tcpdump -i "$NETWORK_IFACE" $PCAP_FILTER -w "$TRACE_FILENAME" &
    DUMP_PROCESS_ID=$!
    sleep 0.5

    # Send the query (suppress output)
    python3 client.py grid $cell_id -T restaurant > /dev/null

    sleep 0.5
    kill $DUMP_PROCESS_ID
    wait $DUMP_PROCESS_ID 2>/dev/null || true

    echo "  ✔ Saved $TRACE_FILENAME"
    sleep 0.2
  done

  # Restart Tor to randomize circuits
  sv restart tor
  sleep 1
done

echo "✅ All trace captures complete."
