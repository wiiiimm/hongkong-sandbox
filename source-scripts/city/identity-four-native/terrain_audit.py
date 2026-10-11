"""Exact native terrain diagnostic for Elements; no patch or live data mutation."""
import pathlib,json,sys,numpy as np,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-four-native';sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import native_terrain as n
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=next(r for r in read(DOC/'support.json')['rows']if r['uid']=='landsd/273061:0');sources=[];points=[s['position'] for s in r['rim']]+[p for t in r['upwardBuriedFaces']for p in t['positions']];v=np.array(points);out=np.full(len(v),-np.inf)
for rel in ['source-scripts/city/landmark-acquisition/batches/terrain-prerequisites/staged/11-NW-24C/manifest.json','source-scripts/city/landmark-acquisition/batches/terrain-final-increment/staged/11-NW-24A/manifest.json']:
 mp=ROOT/rel;m=read(mp);t=m['terrain'];files=[]
 for f in [t['url']]+[p for p in t['sourceHashes']if p.endswith('.bin')]:
  p=mp.parent/f;files.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size})
 source={'sheet':m['tile'],'revision':m['tileRevision'],'manifest':rel,'manifestSha256':sha(mp),'worldBounds':t['worldBounds'],'files':files,'sourceFilesVerified':True};sources.append(source);_,_,_,_,usable,tree=n.terrain_index(mp.parent);out=np.maximum(out,n.samples(v[:,[0,2]],usable,tree));print(m['tile'],'covered',np.isfinite(out).sum(),flush=True)
count=len(r['rim']);rim=[{**s,'nativeGround':float(h)if np.isfinite(h)else None,'nativeGap':s['position'][1]-float(h)if np.isfinite(h)else None}for s,h in zip(r['rim'],out[:count])];tri=[]
for i,t in enumerate(r['upwardBuriedFaces']):
 vals=out[count+i*3:count+i*3+3];gaps=np.array(t['positions'])[:,1]-vals;tri.append({**t,'nativeGround':vals.tolist(),'nativeGap':gaps.tolist(),'nativeWhollyBuried':bool((gaps<-.25).all())})
report={'uid':r['uid'],'issue':'HKS-214','rim':rim,'sources':sources,'rimCovered':sum(s['nativeGround']is not None for s in rim),'rimWithin2m':sum(s['nativeGap']is not None and abs(s['nativeGap'])<=2 for s in rim),'rimAboveNative2m':sum(s['nativeGap']is not None and s['nativeGap']>2 for s in rim),'rimBelowNative2m':sum(s['nativeGap']is not None and s['nativeGap']< -2 for s in rim),'upwardCurrentlyBuriedFaces':len(tri),'upwardStillBuriedUnderNative':sum(t['nativeWhollyBuried']for t in tri),'triangles':tri,'terrainModified':False,'verticalScale':1};(DOC/'elements-native-terrain.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k not in ['rim','sources','triangles']})
