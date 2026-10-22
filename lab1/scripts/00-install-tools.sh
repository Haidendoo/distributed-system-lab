#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
case "$(uname -m)" in
  x86_64) arch=amd64 ;;
  aarch64|arm64) arch=arm64 ;;
  *) echo 'Supported architectures: amd64, arm64' >&2; exit 1 ;;
esac
[[ "$(uname -s)" == Linux ]] || { echo 'Run in Linux or WSL2.' >&2; exit 1; }
command -v docker >/dev/null
docker info >/dev/null
mkdir -p "$LAB_DIR/.bin"
download_dir=$(mktemp -d)
trap 'rm -rf "$download_dir"' EXIT
curl -fsSL --connect-timeout 15 --max-time 60 --retry 2 "https://github.com/k3d-io/k3d/releases/download/v5.8.3/checksums.txt" -o "$download_dir/checksums.txt"
expected=$(awk -v name="_dist/k3d-linux-$arch" '$2 == name {print $1}' "$download_dir/checksums.txt")
[[ -n "$expected" ]]
install_verified() {
  local name="$1" checksum="$2" url="$3"
  if [[ -x "$LAB_DIR/.bin/$name" ]] && \
      printf '%s  %s\n' "$checksum" "$LAB_DIR/.bin/$name" | sha256sum -c --status -; then
    echo "$name: existing binary matches official checksum"
    return
  fi
  curl -fL --connect-timeout 15 --max-time 600 --retry 2 "$url" -o "$download_dir/$name"
  printf '%s  %s\n' "$checksum" "$download_dir/$name" | sha256sum -c -
  install -m 0755 "$download_dir/$name" "$LAB_DIR/.bin/$name"
}
install_verified k3d "$expected" "https://github.com/k3d-io/k3d/releases/download/v5.8.3/k3d-linux-$arch"
curl -fsSL --connect-timeout 15 --max-time 60 --retry 2 "https://dl.k8s.io/release/v1.34.1/bin/linux/$arch/kubectl.sha256" -o "$download_dir/kubectl.sha256"
install_verified kubectl "$(cat "$download_dir/kubectl.sha256")" "https://dl.k8s.io/release/v1.34.1/bin/linux/$arch/kubectl"
k3d version
kubectl version --client
