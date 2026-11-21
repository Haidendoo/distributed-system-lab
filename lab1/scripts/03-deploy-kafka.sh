#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_cluster
kubectl apply -f "$LAB_DIR/k8s/kafka.yaml"
kubectl -n kafka rollout status statefulset/kafka --timeout=600s
kubectl -n kafka get pods,pvc -o wide
kubectl -n kafka exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka-service:9092 --create --if-not-exists \
  --topic lab1-demo --partitions 3 --replication-factor 2
kubectl -n kafka exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka-service:9092 --describe --topic lab1-demo
