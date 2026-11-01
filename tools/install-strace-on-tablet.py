#!/usr/bin/env python3
"""Copy a 32-bit musl strace (+libs) from Alpine edge x86 onto the booted tablet: PMOS_PASSWORD=... install-strace-on-tablet.py
Then on the tablet: LD_LIBRARY_PATH=/tmp/stl/usr/lib:/tmp/stl/lib /tmp/strace -f -e trace=execve <cmd>
Versions are looked up in Alpine's APKINDEX, nothing is hardcoded."""
import io, os, subprocess, sys, tarfile, tempfile, urllib.request, pexpect
BASE = 'https://dl-cdn.alpinelinux.org/alpine/edge/main/x86/'
WANT = ['strace', 'libdw', 'libelf', 'musl-fts']
idx = tarfile.open(fileobj=io.BytesIO(urllib.request.urlopen(BASE + 'APKINDEX.tar.gz').read())).extractfile('APKINDEX').read().decode()
ver = {}
for blk in idx.split('\n\n'):
    f = dict(l.split(':', 1) for l in blk.split('\n') if ':' in l)
    if f.get('P') in WANT: ver[f['P']] = f['V']
with tempfile.TemporaryDirectory() as t:
    for p in WANT:
        data = urllib.request.urlopen(f'{BASE}{p}-{ver[p]}.apk').read()
        tarfile.open(fileobj=io.BytesIO(data)).extractall(t, filter='tar')  # apk = gzip tar
    dirs = [d for d in ('usr', 'lib') if os.path.isdir(os.path.join(t, d))]
    subprocess.run(['tar', '-czf', '/tmp/stl-pack.tgz', '-C', t] + dirs, check=True)
    def run(cmd):
        c = pexpect.spawn(cmd[0], cmd[1:], encoding='utf-8', timeout=180)
        c.expect('assword'); c.sendline(os.environ['PMOS_PASSWORD']); c.expect(pexpect.EOF)
    opts = ['-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'LogLevel=ERROR']
    user = os.environ.get('PMOS_USER', 'wskellenger') + '@172.16.42.1'
    run(['scp'] + opts + ['/tmp/stl-pack.tgz', user + ':/tmp/s.tgz'])
    run(['ssh'] + opts + [user, 'mkdir -p /tmp/stl && tar -xzf /tmp/s.tgz -C /tmp/stl && cp /tmp/stl/usr/bin/strace /tmp/strace'])
print('installed:', ver)
