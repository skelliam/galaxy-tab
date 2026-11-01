#!/usr/bin/env python3
"""Write colour bars with a white border straight to /dev/fb0 (run on the tablet as root, X not running).
Tells you whether the panel works independent of X: red green blue white yellow magenta, white frame."""
import os, struct
W, H, STRIDE = 1280, 800, 5120
cols = [(255,0,0), (0,255,0), (0,0,255), (255,255,255), (255,255,0), (255,0,255)]
rows = []
for y in range(H):
    row = bytearray()
    for x in range(W):
        c = (255,255,255) if y < 20 or y >= H-20 or x < 20 or x >= W-20 else cols[(x-20) * len(cols) // (W-40)]
        row += struct.pack('BBBB', c[2], c[1], c[0], 0)
    rows.append(bytes(row).ljust(STRIDE, b'\0'))
fd = os.open('/dev/fb0', os.O_WRONLY); os.write(fd, b''.join(rows)); os.close(fd)
