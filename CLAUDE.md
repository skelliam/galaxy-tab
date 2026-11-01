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

## Flashing (done 2026-10-31)
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
- Native Linux works (2026-10-31, Linux Mint 22.2 booted on the same PC; Windows drive mounted at
  `/media/wskellenger/F270CC0670CBD011`). Heimdall 2.2.2 built from https://git.sr.ht/~grimler/Heimdall
  (tag v2.2.2, `-DDISABLE_FRONTEND=ON`, CMake from the Kitware tarball since cmake isn't installed) and put
  in `~/.local/bin/heimdall`. No sudo needed: the stock 51-android udev rule gives plugdev access to 04e8.
  Images copied to `~/santos10-flash/` (checksums verified).
- `print-pit` succeeded natively (saved to `~/santos10-flash/pit.txt`), with 512 B blocks: BOOT = 40960 blocks
  (20 MiB, boot.img 16 MiB fits), SYSTEM = 4833280 blocks (2360 MiB, rootfs 2070 MB fits).
- After `print-pit --no-reboot`, the next Heimdall command fails ("Protocol initialisation failed", and
  `--resume` ends right after "Beginning session"). Power-cycle back into download mode before flashing.

## First-boot findings (2026-10-31/11-01)
- The bootloader ignores the cmdline in boot.img (kernel gets Samsung's own, no `pmos_*` / `pmos.debug-shell`).
  The initramfs still finds the rootfs by label, so booting works.
- FIXED in a hand-patched boot image only: initramfs `mount_subpartitions` runs `losetup --direct-io=on`;
  on kernel 3.4.34 the first write through loop0 (parted resize) oopses in `get_user_pages_fast` (NULL deref)
  and boot hangs on the Samsung logo. Removing the flag lets resize and mount work. Needs a permanent fix
  (e.g. an initramfs hook that wraps `losetup` to drop the flag) in pmaports-santos10wifi.
- CURRENT BLOCKER: the rootfs ships systemd 262, which cannot run on kernel 3.4.34 (no cgroup v2; v1 support
  was removed in systemd 258). After switch_root nothing comes up (no journal written, sshd never starts),
  and the screen stays on the bootloader's Samsung logo. Next: re-run `pmbootstrap init` with OpenRC
  instead of systemd, rebuild, reflash SYSTEM.
- Debug method that works: patch the initramfs by appending a cpio overlay (replacement `init_2nd.sh` /
  `init_functions.sh`) to the ramdisk inside boot.img and rewrite the header size + SHA1. Telnet (172.16.42.1:23)
  in `init_2nd.sh` right after `start_unudhcpd`, and a pause before `Switching root`, give a root shell with
  `/sysroot` mounted. The tablet appears on the host as an RNDIS NIC (18d1:d001); host side is 172.16.42.2.
- Fb is `psbfb` 1280x800 and `/dev/dri/card0` exists in the initramfs.

## OpenRC image findings (2026-11-01)
- The OpenRC image boots fully on the 3.4.34 kernel: the losetup hook works (no oops, resize + mount fine),
  OpenRC runs, sshd and lightdm/Xorg start. Debug method: flash a boot image whose ramdisk has a cpio overlay with
  telnet + a pause before `Switching root` (`/tmp/go`), inspect `/sysroot` over telnet at 172.16.42.1:23.
- Found and hot-fixed on the tablet (and now in device-samsung-santos10wifi r3, NOT yet built or flashed):
  1. openssh-server-pam (10.6_p1) ships only `sshd.pam`, `sshd-session.pam`, `sshd-auth.pam`; nothing creates the
     plain names, so sshd never started. Fix: apk trigger `device-samsung-santos10wifi.trigger`.
  2. lightdm waited for a graphical logind seat, never started X. Fix: `71-lightdm-santos10wifi.conf` drop-in with
     `logind-check-graphical=false` (replaces the manual lightdm.conf edit from the wiki).
- With those fixed, `wskellenger@172.16.42.1` works over SSH (USB RNDIS, host side 172.16.42.2) and Xorg starts,
  but the screen stays BLACK (framebuffer all zeros). Not the backlight: sysfs `brightness` reads -1 at boot but the
  panel is lit; that is just the driver's initial value. Cause: slick-greeter aborts in GTK because gdk-pixbuf 2.44
  loads images through glycin, which needs `memfd_create` + `F_ADD_SEALS` (Linux 3.17); kernel 3.4.34 returns ENOSYS
  ("Libc error: ENOSYS" in /var/log/lightdm/seat0-greeter.log, needs root). Fix: `memfd_create-backport.patch` in
  linux-samsung-santos10wifi r3 (untested, not yet built). Other 3.17+ syscalls may surface next.
- The tablet once powered off ~1 min after boot (Samsung charging icon), probably a flat battery after hours of
  debugging on USB power; charge it before long sessions.
- Images in `~/santos10-flash/`: boot.img/rootfs.img = OpenRC (current), *-systemd.img = old, boot-openrc-debug.img =
  debug overlay build. `rootfs.raw`/`root.ext4` in the session scratchpad can be inspected with `debugfs`.

## Tools (`tools/`)
- `build.sh`: pmbootstrap build of kernel, firmware, device package, then `install` (asks for sudo).
- `mk-debug-boot.py in.img out.img`: debug copy of boot.img with a telnet root shell (172.16.42.1:23) and a pause
  before switch_root (`touch /tmp/go` to continue). Flash with `heimdall flash --BOOT out.img`.
- `ssh-tablet.py 'cmd' [--sudo]` (needs `PMOS_PASSWORD`), `watch-boot.sh`, `unsparse.py` (sparse rootfs -> raw,
  then `dd` the root partition and read it with `debugfs`, no root needed).
- Work in progress (2026-11-01): packages `device-samsung-santos10wifi` r3 and `linux-samsung-santos10wifi` r3
  (memfd_create backport) are committed but their first boot is still untested; see the OpenRC findings above.

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
- [x] `print-pit` check from native Linux: BOOT and SYSTEM exist and are big enough.
- [x] Flashed BOOT and SYSTEM from native Linux with Heimdall 2.2.2 (2026-10-31, ~6 min, both uploads successful).
- [x] Rebuilt with OpenRC (2026-11-01, pmbootstrap set up natively on the Mint install, pmaports pinned to 03e1f7d0f4);
      device-samsung-santos10wifi r2 adds the losetup initramfs hook. Verified in the images: hook present, no systemd.
- [ ] Flash the OpenRC boot.img + rootfs.img, then first boot: apply the lightdm fix above, test Wi-Fi/touch, record results here.
- [ ] Write a setup script/README so someone else can reproduce this without the conversation.

## Rules
- Nothing is flashed to the tablet without the user's explicit go-ahead.
- Do not guess at hardware support; check the wiki table or test on device and record results here.
