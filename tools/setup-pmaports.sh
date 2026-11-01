#!/bin/bash
# Prepare pmbootstrap for this device after `./pmbootstrap.py init` (see CLAUDE.md "Build recipe"):
# pin pmaports to the last commit that matches the frozen pmOS x86 binaries and copy our packages in.
# Re-run it after editing anything under pmaports-santos10wifi/. NEVER run `pmbootstrap pull` afterwards.
set -e
PIN=${PIN:-03e1f7d0f4}
R=$(cd "$(dirname "$0")/.." && pwd)
P=~/.local/var/pmbootstrap/cache_git/pmaports
[ -d "$P" ] || { echo "run ~/pmbootstrap/pmbootstrap.py init first (channel edge, samsung/santos10wifi, openrc)"; exit 1; }
[ -d "$R/pmaports-santos10wifi/device" ] || git -C "$R" submodule update --init pmaports-santos10wifi
git -C "$P" checkout -q -f -B main "$PIN"
cp -r "$R"/pmaports-santos10wifi/device/archived/*-samsung-santos10wifi "$P"/device/archived/
for p in linux device firmware; do ~/pmbootstrap/pmbootstrap.py checksum $p-samsung-santos10wifi >/dev/null; done
echo "pmaports pinned to $PIN, packages copied and checksummed"
