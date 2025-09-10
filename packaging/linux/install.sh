#!/usr/bin/env bash
set -euo pipefail

SERVICE_FILE="hermes.service"
TARGET="/etc/systemd/system/${SERVICE_FILE}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "${SCRIPT_DIR}/${SERVICE_FILE}" "${TARGET}"

systemctl daemon-reload
systemctl enable hermes
systemctl start hermes

