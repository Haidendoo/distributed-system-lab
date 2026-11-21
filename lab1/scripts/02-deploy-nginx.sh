#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_cluster
kubectl apply -f "$LAB_DIR/k8s/nginx.yaml"
kubectl -n lab1 rollout status deployment/web-app --timeout=180s
kubectl -n lab1 get pods -o wide
kubectl -n lab1 get service web-app
curl --fail --retry 10 --retry-connrefused --retry-delay 2 http://127.0.0.1:8080/
