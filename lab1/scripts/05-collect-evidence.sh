#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_cluster
output="$LAB_DIR/evidence/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$output"
kubectl get nodes -o wide > "$output/nodes.txt"
kubectl get pods -A -o wide > "$output/pods.txt"
kubectl -n lab1 get svc > "$output/nginx-service.txt"
curl --fail http://127.0.0.1:8080/ > "$output/nginx.html"
kubectl -n kafka get sts,svc,pvc -o wide > "$output/kafka-resources.txt"
kubectl -n kafka exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka-service:9092 --describe --topic lab1-demo > "$output/topic.txt"
kubectl -n kafka exec deployment/kafka-client -- python smoke.py > "$output/python-smoke.txt"
echo "Evidence: $output"
