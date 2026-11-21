#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
require_cluster
echo 'Kafka UI: http://localhost:8081 (Ctrl+C to stop forwarding)'
exec kubectl -n kafka port-forward --address 127.0.0.1 service/kafka-ui 8081:8080
