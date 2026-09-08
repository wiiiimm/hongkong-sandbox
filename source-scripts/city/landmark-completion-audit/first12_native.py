"""Compare every presently hidden source triangle with native TIN; no asset edits."""
import sys,pathlib,json,numpy as np,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import native_terrain as native
D=ROOT/'docs/astra-city/landmark-completion-audit';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=read(ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json')['nativeSources'];report=read(D/'first12-surfaces.json');models=read(ROOT/'source-scripts/city/landmark-completion-audit/first12-catalogue.json')['models'];bounds={m['uid']:m['worldBounds'] for m in models};jobs={};used={}
 for row in report['rows']:
  faces=row['stats']['patched']['buriedTriangleEvidence']
  if not faces:continue
  tri=np.array([t['positions'] for t in faces]);points=tri.reshape(-1,3)[:,[0,2]];jobs[row['uid']]={'tri':tri,'faces':faces,'points':points,'height':np.full(len(points),-np.inf)}
 for s in source:
  b=s['worldBounds'];targets=[(u,j) for u,j in jobs.items() if j['points'][:,0].max()>=b[0][0] and j['points'][:,0].min()<=b[1][0] and j['points'][:,1].max()>=b[0][2] and j['points'][:,1].min()<=b[1][2]]
  if not targets:continue
  assert sha(ROOT/s['manifest'])==s['manifestSha256']
  for f in s['files']:assert sha(ROOT/f['path'])==f['sha256']
  *_,usable,tree=native.terrain_index((ROOT/s['manifest']).parent);used[s['sheet']]=s
  for u,j in targets:j['height']=np.maximum(j['height'],native.samples(j['points'],usable,tree))
 rows=[]
 for u,j in jobs.items():
  t=j['tri'];nativeY=j['height'].reshape(-1,3);ys=t[:,:,1];gaps=ys-nativeY;hidden=(gaps<-.25).all(axis=1);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normal,axis=1);up=np.divide(normal[:,1],length,out=np.zeros(len(length)),where=length>0)>.15
  rows.append({'uid':u,'currentWhollyBuriedTriangles':len(t),'nativeCoveredVertices':int(np.isfinite(nativeY).sum()),'vertices':nativeY.size,'nativeStillWhollyBuriedTriangles':int(hidden.sum()),'currentUpwardBuriedTriangles':int(up.sum()),'nativeStillUpwardBuriedTriangles':int((hidden&up).sum()),'currentHiddenArea':float(length.sum()/2),'nativeStillHiddenArea':float(length[hidden].sum()/2),'nativeHiddenHeightRange':[float(ys[hidden].min()),float(ys[hidden].max())] if hidden.any() else None,'nativeGapRange':[float(gaps[np.isfinite(gaps)].min()),float(gaps[np.isfinite(gaps)].max())],'nativeUncoveredVertices':int((~np.isfinite(nativeY)).sum()),'nativeComparedEvidence':[{'positions':p.tolist(),'nativeGround':[float(x) if np.isfinite(x) else None for x in n],'gaps':[float(x) if np.isfinite(x) else None for x in g],'stillHidden':bool(h),'upward':bool(v)} for p,n,g,h,v in zip(t,nativeY,gaps,hidden,up)]})
 out={'issue':'HKS-214','method':'Native source TIN barycentric heights at all vertices of every triangle hidden by current rendered terrain. No extrapolation, no source geometry edits, 1x HKPD. Native burial remains a diagnostic requiring architecture context.','sources':list(used.values()),'rows':rows};(D/'first12-native-burial.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k!='nativeComparedEvidence'} for r in rows],indent=2))
if __name__=='__main__':main()
