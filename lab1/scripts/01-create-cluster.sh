#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
docker info >/dev/null
if k3d cluster list -o json | python3 -c 'import json,sys; sys.exit(not any(c["name"] == "ds-lab1" for c in json.load(sys.stdin)))'; then
  echo 'Cluster ds-lab1 exists; reusing it.'
else
  k3d cluster create --config "$LAB_DIR/k3d.yaml"
fi
umask 077
k3d kubeconfig get ds-lab1 > "$KUBECONFIG"
require_cluster
kubectl wait --for=condition=Ready node --all --timeout=180s
kubectl -n kube-system rollout status deployment/coredns --timeout=180s
kubectl -n kube-system rollout status deployment/local-path-provisioner --timeout=180s
kubectl get nodes -o wide
kubectl get pods -A
kubectl get storageclass
