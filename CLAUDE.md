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
- The APKBUILD's kernel source URL (github.com/dpdudek/android_kernel_samsung_santos10) is a 404.
  Same commit edec7f67e953eff11415ac47b6a5080e6e8b2ffe exists at
  https://github.com/santos10-dev/android_kernel_samsung_santos10 and the tarball sha512 matches the
  APKBUILD, so just change the URL (no checksum change). Risk: 3.4 kernel with patches only up to gcc10;
  may not build with current Alpine gcc.
- Our public repos (GitHub user `skelliam`):
  - https://github.com/skelliam/android_kernel_samsung_santos10 (submodule `./kernel`, shallow; fork of santos10-dev; branch `pmos-santos10`
    at edec7f67, put kernel fixes here as commits)
  - https://github.com/skelliam/pmaports-santos10wifi (the 3 archived packages, kernel URL fixed, shared gcc
    patches vendored as real files; submodule `./pmaports-santos10wifi`)
- No tablet data needs backing up (user confirmed).

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
- [x] pmbootstrap cloned to `~/pmbootstrap` (nothing run yet).
- [ ] User reads wiki feature table (display, touch, Wi-Fi, USB, GPU, suspend) and confirms it is worth it.
- [ ] `./pmbootstrap.py init` (samsung / santos10wifi / xfce4 or none) and `install`.
- [ ] Work out the flash method (wiki install section) and USB access from WSL2 (`usbipd-win`) or Windows.
- [ ] Back up the tablet's data before flashing. Flashing wipes it.

## Rules
- Nothing is flashed to the tablet without the user's explicit go-ahead.
- Do not guess at hardware support; check the wiki table or test on device and record results here.
