"""Small deterministic comparison contact sheets and a portable replay bundle."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile
import numpy as np
from PIL import Image, ImageDraw
from shape_metrics import mesh, frame, POLICY
from shape_screen import ROOT, HERE, read, save


def panels(data,size=192):
    a,b=mesh(data['current']),mesh(data['candidate']);result=[]
    for az,el in [(45,40),(0,90)]:
        x,y,pixel=frame(a,b,az,el,size);ma,mb=np.isfinite(x),np.isfinite(y);values=np.r_[x[ma],y[mb]]
        low,high=values.min(),values.max();span=max(1e-6,high-low)
        images=[]
        for depths,mask in [(x,ma),(y,mb)]:
            colors=np.full((size,size,3),245,dtype=np.uint8)
            tone=np.zeros_like(depths);tone[mask]=(depths[mask]-low)/span
            colors[mask]=np.stack([70+110*tone[mask],100+100*tone[mask],110+100*tone[mask]],axis=1).astype(np.uint8)
            images.append(Image.fromarray(np.flipud(colors)))
        colors=np.full((size,size,3),245,dtype=np.uint8);colors[ma&mb]=[205,213,216]
        colors[ma&~mb]=[63,119,201];colors[mb&~ma]=[210,75,69]
        overlap=ma&mb;changed=np.zeros_like(ma);changed[overlap]=np.abs(x[overlap]-y[overlap])>max(.1,pixel*POLICY['pixelDepthTolerance'])
        colors[changed]=[224,166,38];images.append(Image.fromarray(np.flipud(colors)))
        result.append(images)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'docs/astra-city/enhancement-screening/shape-pilot-1000');p.add_argument('--geometry',type=Path,default=HERE/'local/shapes/geometry');p.add_argument('--evidence',type=Path,default=HERE/'local/shape-inputs.json.gz');p.add_argument('--no-contact-sheets',action='store_true');a=p.parse_args()
    rows=json.loads(gzip.decompress((a.out/'results.json.gz').read_bytes()));idx=read(a.geometry/'index.json');by_uid={r['uid']:r for r in idx['rows']};groups=defaultdict(list)
    for r in rows:
        if r['metrics']:groups[r['comparison']].append(r)
    selected=[]
    for kind,items in sorted(groups.items()):
        selected.extend(sorted(items,key=lambda r:hashlib.sha256(r['uid'].encode()).hexdigest())[:4])
    if a.no_contact_sheets:selected=[]
    files=[]
    for start in range(0,len(selected),4):
        group=selected[start:start+4];canvas=Image.new('RGB',(1240,90+235*len(group)),(250,250,250));draw=ImageDraw.Draw(canvas)
        draw.text((20,12),'SCRIPTED SHAPE COMPARISON - fixed geometry views; not architectural acceptance',fill=(20,30,40))
        draw.text((20,32),'Blue: current only. Red: government only. Gold: depth differs. Shading indicates depth, not materials.',fill=(40,50,60))
        for i,label in enumerate(['Current / oblique','Government / oblique','Difference','Current / roof','Government / roof','Difference']):draw.text((20+203*i,62),label,fill=(20,30,40))
        for j,r in enumerate(group):
            y=90+j*235;draw.text((20,y),f"{r['uid']}  {r['name'][:34]}  | {r['comparison']} | {r['action']}",fill=(20,30,40))
            d=json.loads(gzip.decompress((a.geometry/by_uid[r['uid']]['file']).read_bytes()));images=[im for trio in panels(d) for im in trio]
            for i,im in enumerate(images):canvas.paste(im,(20+203*i,y+24))
        file=f'comparison-{start//4+1}.jpg';canvas.save(a.out/file,quality=88);files.append(file)
    # Retain only current index members, excluding obsolete local geometry/cache files.
    contents=['index.json']+[r['file'] for r in idx['rows'] if 'file' in r]
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as tar:
        for name in sorted(set(contents)):
            raw=(a.geometry/name).read_bytes();info=tarfile.TarInfo(name);info.size=len(raw);info.mtime=0;info.mode=0o644;tar.addfile(info,io.BytesIO(raw))
    packed=gzip.compress(buffer.getvalue(),mtime=0);(a.out/'geometry.tar.gz').write_bytes(packed)
    shutil.copyfile(a.evidence,a.out/'inputs.json.gz')
    save(a.out/'replay-manifest.json',{'geometrySHA256':hashlib.sha256(packed).hexdigest(),'geometryBytes':len(packed),'inputSHA256':hashlib.sha256((a.out/'inputs.json.gz').read_bytes()).hexdigest(),'pairs':len(contents)-1,'contactSheets':files,'contactUids':[r['uid'] for r in selected],'source':'Exact original government geometry through the existing City loader; current geometry through the City building builder. No model changes or AI modelling.'})
    print(json.dumps({'pairs':len(contents)-1,'bytes':len(packed),'contactSheets':files}))

if __name__=='__main__':main()
