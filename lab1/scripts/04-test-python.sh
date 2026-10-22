#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_cluster
kubectl -n kafka create configmap kafka-client-code --from-file="$LAB_DIR/clients/" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "$LAB_DIR/k8s/client.yaml"
# Refresh mounted code and dependencies immediately on subsequent runs.
kubectl -n kafka rollout restart deployment/kafka-client
kubectl -n kafka rollout status deployment/kafka-client --timeout=300s
kubectl -n kafka exec deployment/kafka-client -- python producer.py
kubectl -n kafka exec deployment/kafka-client -- python consumer.py \
  --group "demo-$(date +%s)-$RANDOM" --count 10 --timeout 60
kubectl -n kafka exec deployment/kafka-client -- python smoke.py
