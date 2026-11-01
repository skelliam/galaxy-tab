#!/bin/bash
# Build kernel + device package and produce boot.img/rootfs.img. Needs sudo (pmbootstrap asks).
# Prereqs: see "Build recipe" in CLAUDE.md (pmaports pinned, our packages copied in).
set -e
cd ~/pmbootstrap
./pmbootstrap.py build linux-samsung-santos10wifi
./pmbootstrap.py build firmware-samsung-santos10wifi
./pmbootstrap.py build device-samsung-santos10wifi
./pmbootstrap.py install
