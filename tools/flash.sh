#!/bin/bash
# Flash boot.img (BOOT) and rootfs.img (SYSTEM) to the Galaxy Tab 3 10.1 Wi-Fi. Usage: flash.sh [dir with boot.img rootfs.img]
# Put the tablet in download mode first: power off, hold Power + Vol Down, then Vol Up at the warning.
# Bootloader, recovery (TWRP) and userdata are not touched. Do NOT run `heimdall print-pit` right before this:
# it leaves a dirty session and the next heimdall command fails (power-cycle into download mode if that happens).
set -e
D=${1:-$PWD}; H=${HEIMDALL:-heimdall}
for f in boot.img rootfs.img; do [ -f "$D/$f" ] || { echo "missing $D/$f"; exit 1; }; done
lsusb | grep -q '04e8:685d' || { echo "tablet not found in download mode (USB 04e8:685d)"; exit 1; }
[ -f "$D/SHA256SUMS" ] && (cd "$D" && sha256sum -c SHA256SUMS)
read -r -p "This replaces the OS on the tablet (Android/LineageOS). Continue? [y/N] " a; [ "$a" = y ] || exit 1
cd "$D" && "$H" flash --BOOT boot.img --SYSTEM rootfs.img
