#!/bin/bash
# Local health summary (read it with Oracle "Run command": cat /opt/maiga/logs/status.txt)
echo "updated: $(date -u +%FT%TZ)"; echo "uptime: $(uptime -p)"; echo "load: $(cut -d' ' -f1-3 /proc/loadavg)"
free -m | awk '/Mem:/{print "memory: "$3" MB used of "$2" MB"}'; df -h / | awk 'NR==2{print "disk: "$3" used of "$2}'
echo "code: $(git -C /opt/maiga/repo rev-parse --short HEAD)"; echo; echo "site:"; tail -n 6 /opt/maiga/logs/sitewatch.log
