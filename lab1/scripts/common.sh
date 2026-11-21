#!/usr/bin/env bash
set -euo pipefail
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$LAB_DIR/.bin:$PATH"
# Always use the lab's isolated kubeconfig, never the user's current cluster.
export KUBECONFIG="$LAB_DIR/.kubeconfig"
require_cluster() {
  [[ -s "$KUBECONFIG" ]] || { echo 'Run step 01 first.' >&2; exit 1; }
  [[ "$(kubectl config current-context)" == k3d-ds-lab1 ]] || {
    echo 'Unexpected Kubernetes context; expected k3d-ds-lab1.' >&2; exit 1;
  }
  kubectl cluster-info >/dev/null
}
