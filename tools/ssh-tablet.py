#!/usr/bin/env python3
"""Run a command on the tablet over USB networking: PMOS_PASSWORD=... ssh-tablet.py 'uname -a' [--sudo]"""
import os, sys, pexpect
cmd = sys.argv[1]
if '--sudo' in sys.argv:
    cmd = "sudo -S sh -c '%s'" % cmd
c = pexpect.spawn('ssh', ['-tt', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'LogLevel=ERROR',
                          os.environ.get('PMOS_USER', 'wskellenger') + '@172.16.42.1', cmd], encoding='utf-8', timeout=60)
c.expect('assword'); c.sendline(os.environ['PMOS_PASSWORD'])
if '--sudo' in sys.argv:
    c.expect('assword'); c.sendline(os.environ['PMOS_PASSWORD'])
c.expect(pexpect.EOF)
print(c.before.replace('\r', '').strip())
