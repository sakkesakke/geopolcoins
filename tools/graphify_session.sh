#!/usr/bin/env bash
# Start of a Claude session: make sure graphify (pinned, Apache-2.0, github.com/safishamsi/graphify) is installed and
# the code graph in graphify-out/ is fresh. Local only: AST parsing, no AI service, nothing leaves the machine.
# Never blocks the session: any failure just means no graph this time.
cd "$(dirname "$0")/.." || exit 0
command -v graphify >/dev/null 2>&1 || pip install -q --disable-pip-version-check --break-system-packages "graphifyy==0.9.106" >/dev/null 2>&1 || pip install -q --user "graphifyy==0.9.106" >/dev/null 2>&1
command -v graphify >/dev/null 2>&1 || exit 0
timeout 90 graphify update . >/dev/null 2>&1
echo "graphify: code graph ready in graphify-out/ (graphify query \"...\" before grep/read)."
exit 0
