# Galaxy Tab 3 10.1 -> native lightweight Linux

## Goal
Replace Android on an old Samsung Galaxy Tab 3 10.1 Wi-Fi with a native, lightweight Linux desktop.
Do NOT run Linux on top of Android (chroot / Linux Deploy / VNC): the user rejected it because Android
is already slow on this device and they want all of the RAM for Linux.
Chosen route: postmarketOS (Alpine-based), device `samsung-santos10wifi`, built with `pmbootstrap`.

## Device facts
- GT-P5210, codename `santos10wifi`, board `clovertrail`. Intel Atom Z2560 (Clover Trail+), 32-bit x86, 1 GB RAM.
- GPU is PowerVR SGX544: no open driver, so expect software rendering only. Keep the desktop light
  (XFCE / Openbox / LXQt, not Phosh / Plasma Mobile).
- Currently runs LineageOS 14.1 (Android 7.1.2), unofficial build 2020-08-08, from
  `C:\Users\wskellenger\Downloads\lineage-14.1-20200808-UNOFFICIAL-santos10wifi.zip`.
  KEEP THIS ZIP: it is the rollback path.
- Android kernel/device source (not official LineageOS): https://github.com/santos10-dev
  (`android_kernel_samsung_santos10`, device trees).
- postmarketOS port page: https://wiki.postmarketos.org/wiki/Samsung_Galaxy_Tab_3_10.1_Wi-Fi_(samsung-santos10wifi)
  Wiki status: ARCHIVED (not in pmbootstrap's device list; type `samsung` / `santos10wifi` manually, kernel
  must be built by us). Vendor kernel 3.4.34, x86. Reported working: touchscreen, Wi-Fi. 3D accel BROKEN
  (software rendering only). Camera, Bluetooth, GPS, sensors untested. Other rows of the pasted feature
  table lost their labels, so display/USB/suspend status is still unconfirmed.
  Only Xfce4 tested (poor performance); Weston broken. lightdm fix needed after first boot:
  `export DISPLAY=:0` in ~/.bashrc, and set `logind-check-graphical=false` in /etc/lightdm/lightdm.conf.
- Package files live in pmaports `device/archived/{device,firmware,linux}-samsung-santos10wifi`
  (last touched in commit cfbc1de3c, 2026-06-22). Flash method: heimdall (`flash_method=heimdall-bootimg`,
  partition BOOT). Download mode: Power + Vol Down from off. Wiki flow:
  `pmbootstrap flasher flash_kernel`, reboot to download mode, `pmbootstrap flasher flash_rootfs`.
- The original APKBUILD kernel URL (github.com/dpdudek/...) is a 404; our packages repo points at the
  skelliam fork instead. The vendor 3.4.34 kernel does build with Alpine's gcc 15 after one fix:
  arch/x86/boot Makefiles reset KBUILD_CFLAGS, so they need `-std=gnu89` (fork commit 6d56daec).
- Our public repos (GitHub user `skelliam`):
  - https://github.com/skelliam/android_kernel_samsung_santos10 (submodule `./kernel`, shallow; fork of santos10-dev; branch `pmos-santos10`
    at 6d56daec = upstream edec7f67 + gnu89 boot fix; put kernel fixes here as commits)
  - https://github.com/skelliam/pmaports-santos10wifi (the 3 archived packages, kernel URL fixed, shared gcc
    patches vendored as real files; submodule `./pmaports-santos10wifi`)
- No tablet data needs backing up (user confirmed).

## Build recipe (what actually worked, 2026-10-31)
postmarketOS no longer publishes 32-bit x86 binaries: stable channels (v26.06 etc.) have none, and the
edge x86 repo is frozen at 2026-09-10 (x86_64/aarch64 update daily). Current pmaports `main` therefore
looks "out of date" to pmbootstrap, which then tries to rebuild systemd etc. and dies with
"Can't resolve build order of remaining packages". Fix: pin pmaports to a commit matching the frozen binaries.
1. `./pmbootstrap.py init`: channel edge, vendor `samsung`, device `santos10wifi`, xfce4, systemd (default).
2. In `~/.local/var/pmbootstrap/cache_git/pmaports`: `git checkout -f -B main 03e1f7d0f4` (2026-09-10).
   Then copy `pmaports-santos10wifi/device/archived/*-samsung-santos10wifi` into its `device/archived/`.
   NEVER run `pmbootstrap pull` (moves pmaports past the pin and brings the error back).
3. `./pmbootstrap.py build linux-samsung-santos10wifi` (~5-10 min) and
   `./pmbootstrap.py build firmware-samsung-santos10wifi` (Wi-Fi firmware; install does NOT build it by itself).
4. `./pmbootstrap.py install` -> `~/.local/var/pmbootstrap/chroot_native/home/pmos/rootfs/samsung-santos10wifi.img`
   (Android sparse image, 1.3 GB, expands to 2070 MB) and
   `~/.local/var/pmbootstrap/chroot_rootfs_samsung-santos10wifi/boot/boot.img` (17 MB).
Caveats: pmOS x86 binaries are from 2026-09-10 but Alpine edge is current, so a soname bump could break
`install` later. Fallback idea: re-run init without systemd (OpenRC, also lighter for 1 GB RAM).

## Flashing (not done yet)
- Download mode: Power + Vol Down from off, then Vol Up. USB id in download mode: 04e8:685d.
- Flash commands (Heimdall): `heimdall flash --BOOT boot.img --no-reboot`, then
  `heimdall flash --SYSTEM rootfs.img`. BOOT = Android boot image (kernel+ramdisk), SYSTEM = rootfs.
  Bootloader, RECOVERY (TWRP is installed) and userdata are NOT touched. Rollback: boot TWRP and
  sideload the Lineage zip.
- Run `heimdall print-pit --no-reboot` first (read-only) to confirm BOOT/SYSTEM exist and SYSTEM >= 2070 MB.
- Images are staged at `C:\Users\wskellenger\Downloads\santos10-flash\` (boot.img sha256 0bd2f1fd...,
  rootfs.img sha256 6600be9c...). Regenerate from the paths above if needed.
- WSL2 + usbipd does NOT work: Heimdall 2.0.2 (apt) and 2.2.2 (pmOS chroot) handshake fine, then bulk-IN
  times out (libusb error -7) after "Beginning session". It also leaves a dirty session, so power-cycle
  into download mode between attempts. pmbootstrap's chroot /dev is a private tmpfs without
  /dev/bus/usb, so `pmbootstrap flasher` cannot see USB devices anyway.
- Next: flash from native USB: Heimdall on Windows (winget `BenjaminDobell.Heimdall` 1.4.0 + Zadig WinUSB
  driver for 04E8:685D, after `usbipd unbind --busid 1-11`) or a native Linux boot (needs Heimdall 2.2.x).

## Environment
- Windows 11 host, WSL2 distro `Ubuntu` (24.04), 16 GB RAM, ample disk.
- pmbootstrap is cloned at `~/pmbootstrap` in WSL; run as `./pmbootstrap.py`. It needs sudo (password
  prompt), so the user runs `init` and `install` themselves; Claude cannot type the password.
- postmarketOS hosts now redirect to `nura.eco` (wiki, GitLab). This is in upstream's own code and
  commits by a real maintainer, so treat it as a project domain move, not a hijack. The wiki is behind
  Anubis bot protection, so automated fetching fails; the user must read it in a browser.
- `~/projects/oss/rea` (REA, reverse engineering MCP) is only useful if a vendor blob (touch, Wi-Fi,
  GPU) needs analysis. Not needed for the basic port.

## Status
- [x] Zip inspected (build.prop, updater-script).
- [x] Wiki read: port is archived but works (touch, Wi-Fi); recorded above.
- [x] Kernel, firmware, device packages build; `install` produced boot.img and rootfs.img (see Build recipe).
- [x] No tablet data needs backing up; TWRP recovery is installed (rollback path).
- [ ] `print-pit` check, then flash BOOT and SYSTEM from native USB (see Flashing). Needs user go-ahead.
- [ ] First boot: apply the lightdm fix above, test Wi-Fi/touch, record results here.
- [ ] Write a setup script/README so someone else can reproduce this without the conversation.

## Rules
- Nothing is flashed to the tablet without the user's explicit go-ahead.
- Do not guess at hardware support; check the wiki table or test on device and record results here.
