#!/bin/bash
# Build Heimdall 2.2.2 (the 2.0.2 in Ubuntu's apt cannot flash this tablet reliably) into ~/.local/bin/heimdall.
# Needs: git, g++, make, libusb-1.0-0-dev, zlib1g-dev (apt). Downloads CMake from Kitware if cmake is missing.
set -e
W=$(mktemp -d); cd "$W"
if ! command -v cmake >/dev/null; then
  v=3.30.5
  curl -sSL -o cmake.tgz "https://github.com/Kitware/CMake/releases/download/v$v/cmake-$v-linux-x86_64.tar.gz"
  mkdir cmake && tar xzf cmake.tgz -C cmake --strip-components=1; export PATH="$W/cmake/bin:$PATH"
fi
git clone -q https://git.sr.ht/~grimler/Heimdall src
git -C src checkout -q v2.2.2
cmake -S src -B build -DCMAKE_BUILD_TYPE=Release -DDISABLE_FRONTEND=ON >/dev/null
cmake --build build -j"$(nproc)"
mkdir -p ~/.local/bin && cp build/bin/heimdall ~/.local/bin/ && ~/.local/bin/heimdall version
# The stock 51-android udev rule already gives the plugdev group access to Samsung (04e8) devices on Mint/Ubuntu.
