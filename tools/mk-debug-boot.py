#!/usr/bin/env python3
"""Make a debug copy of a postmarketOS boot.img: usage mk-debug-boot.py in.img out.img

Appends a cpio overlay to the initramfs that replaces init_2nd.sh with a copy that
  - starts a root telnet shell on 172.16.42.1:23 right after the USB network is up
  - pauses before switch_root until `touch /tmp/go` (rootfs is mounted at /sysroot)
Then `heimdall flash --BOOT out.img`. Pass --no-pause to keep only the telnet shell.
"""
import gzip, hashlib, io, struct, subprocess, sys

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pause = '--no-pause' not in sys.argv
    src, dst = args
    d = open(src, 'rb').read()
    ks, ka, rs, ra, ss, sa, ta, ps = struct.unpack('<8I', d[8:40])
    pad = lambda n: (n + ps - 1) // ps * ps
    kernel = d[ps:ps + ks]
    ramdisk = d[ps + pad(ks):ps + pad(ks) + rs]
    assert ramdisk[:2] == b'\x1f\x8b' and ss == 0, 'expected gzip ramdisk and no second stage'

    init2 = subprocess.run(['cpio', '-i', '--to-stdout', '--quiet', 'init_2nd.sh'], input=gzip.decompress(ramdisk),
                           capture_output=True, check=True).stdout.decode()
    out, done_t, done_p = [], False, False
    for line in init2.splitlines():
        if pause and line == 'echo "Switching root"' and not done_p:
            out += ['while ! [ -e /tmp/go ]; do sleep 1; done  # debug pause']
            done_p = True
        out.append(line)
        if line == 'start_unudhcpd' and not done_t:
            out.append('telnetd -b "${HOST_IP}:23" -l /bin/sh &  # debug shell')
            done_t = True
    assert done_t and (done_p or not pause), 'init_2nd.sh layout changed'

    # cpio needs a real file with the right mode
    import os, tempfile
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, 'init_2nd.sh')
        open(p, 'w').write('\n'.join(out) + '\n'); os.chmod(p, 0o755)
        cpio = subprocess.run(['cpio', '-o', '-H', 'newc', '--owner=0:0', '--quiet'], input=b'init_2nd.sh\n',
                              cwd=t, capture_output=True, check=True).stdout
    ramdisk2 = ramdisk + gzip.compress(cpio, 9)

    hdr = bytearray(d[:ps])
    struct.pack_into('<I', hdr, 16, len(ramdisk2))
    sha = hashlib.sha1()
    for blob in (kernel, ramdisk2, b''):
        sha.update(blob); sha.update(struct.pack('<I', len(blob)))
    hdr[576:608] = sha.digest().ljust(32, b'\0')
    open(dst, 'wb').write(bytes(hdr) + kernel.ljust(pad(ks), b'\0') + ramdisk2.ljust(pad(len(ramdisk2)), b'\0'))
    print('wrote', dst, '(pause %s)' % ('on' if pause else 'off'))

main()
