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
  Search snippet suggested a vendor 3.4.x kernel (unconfirmed).

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
