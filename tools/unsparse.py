# Convert an Android sparse image (pmbootstrap rootfs) to a raw image: unsparse.py in.img out.raw
# The root partition can then be cut out with dd and inspected with debugfs (no root needed).
import struct,sys
src,dst=sys.argv[1:3]
f=open(src,'rb'); o=open(dst,'wb')
magic,major,minor,fh,ch,bs,tb,tc,crc=struct.unpack('<IHHHHIIII',f.read(28))
assert magic==0xED26FF3A
f.seek(fh)
for _ in range(tc):
    t,_,n,tsz=struct.unpack('<HHII',f.read(12)); sz=n*bs
    if t==0xCAC1: 
        left=sz
        while left: b=f.read(min(left,1<<24)); o.write(b); left-=len(b)
    elif t==0xCAC2: o.write((f.read(4))*(sz//4))
    elif t==0xCAC3: o.seek(sz,1)
    else: f.seek(tsz-12,1)
o.truncate(tb*bs); o.close()
