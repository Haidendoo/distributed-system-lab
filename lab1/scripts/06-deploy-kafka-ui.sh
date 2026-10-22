#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_cluster
kubectl apply -f "$LAB_DIR/k8s/kafka-ui.yaml"
kubectl -n kafka rollout status deployment/kafka-ui --timeout=600s
echo 'Kafka UI ready. Run: bash lab1/scripts/07-forward-kafka-ui.sh'
