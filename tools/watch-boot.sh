#!/bin/bash
# Poll the tablet over USB networking, then follow its kernel log over ssh.
while true; do
  if timeout 2 bash -c 'echo > /dev/tcp/172.16.42.1/22' 2>/dev/null; then
    ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "${PMOS_USER:-wskellenger}@172.16.42.1" 'dmesg -w'
  else
    printf '%s  ping:%s  ssh:closed\r' "$(date +%T)" "$(ping -c1 -W1 172.16.42.1 >/dev/null 2>&1 && echo up || echo down)"
  fi
  sleep 2
done
