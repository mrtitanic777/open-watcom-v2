#!/usr/bin/env python3
"""wasm MASM-mode regression harness: assemble each fixture with wasm -zcm=masm,
snapshot the .obj bytes (sha1) as golden. --update writes golden; default checks."""
import sys,os,subprocess,hashlib,json,glob,tempfile
HERE=os.path.dirname(os.path.abspath(__file__))
WASM=os.path.join(HERE,"..","nt386","wasm.exe")
GOLD=os.path.join(HERE,"golden.json")
def asm(f):
    o=tempfile.NamedTemporaryFile(suffix=".obj",delete=False); o.close()
    r=subprocess.run([WASM,"-zcm=masm","-q","-fo="+o.name,f],capture_output=True,text=True)
    b=open(o.name,"rb").read() if os.path.exists(o.name) else b""
    try: os.unlink(o.name)
    except OSError: pass
    return r.returncode, hashlib.sha1(b).hexdigest(), len(b), (r.stdout+r.stderr)
def run(update=False):
    gold=json.load(open(GOLD)) if os.path.exists(GOLD) else {}
    new={}; fails=0
    for f in sorted(glob.glob(os.path.join(HERE,"fixtures","*.asm"))):
        n=os.path.basename(f); rc,h,sz,log=asm(f)
        new[n]={"rc":rc,"sha1":h,"size":sz}
        if update: print("REC %-22s rc=%d size=%d"%(n,rc,sz)); continue
        g=gold.get(n)
        if not g: print("NEW %s (no golden)"%n); continue
        if g["rc"]!=rc or g["sha1"]!=h:
            print("FAIL %-22s rc %d->%d size %d->%d"%(n,g["rc"],rc,g["size"],sz)); fails+=1
        else: print("PASS %-22s (rc=%d size=%d)"%(n,rc,sz))
    if update:
        json.dump(new,open(GOLD,"w"),indent=1); print("golden written:",len(new))
    else:
        print("\n%d fixtures, %d FAIL"%(len(new),fails)); sys.exit(1 if fails else 0)
run("--update" in sys.argv)
