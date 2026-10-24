"""Exact native-TIN coverage at runtime-decoded vertices, centres, roofs and low rims."""
import sys,json,gzip,hashlib,gc,collections,pathlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import native_terrain as n
read=lambda p:json.loads(p.read_bytes());selection=read(DOC/'selection.json');report=read(DOC/'support.json');rows={p['uid']:p for p in report['rows']};parts={p['uid']:p for p in selection['parts']};meshes=read(DOC/'native-meshes.json');sources=read(ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json')['nativeSources'];work={}
for spec in meshes['rows']:
 raw=(ROOT/spec['cache']).read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['cacheSHA256'];m=json.loads(gzip.decompress(raw));pos=np.array(m['position']).reshape(-1,3);tri=pos[np.array(m['index'])].reshape(-1,3,3);centres=tri.mean(axis=1);rim=np.array([p['position']for p in rows[spec['uid']]['rim']]);roof=np.array([[p['x'],p['top'],p['z']]for p in rows[spec['uid']]['samples']]);points=np.vstack([pos,centres,rim,roof]);work[spec['uid']]={'spec':spec,'pos':pos,'tri':tri,'points':points,'native':np.full(len(points),-np.inf),'sources':[],'lengths':[len(pos),len(centres),len(rim),len(roof)]}
def overlaps(a,b):return a[0][0]<=b[1][0] and b[0][0]<=a[1][0] and a[0][2]<=b[1][2] and b[0][2]<=a[1][2]
for source in sources:
 selected=[(u,w)for u,w in work.items()if overlaps(source['worldBounds'],parts[u]['candidate']['worldBounds'])]
 if not selected:continue
 assert n.sha(ROOT/source['manifest'])==source['manifestSha256']
 for f in source['files']:assert n.sha(ROOT/f['path'])==f['sha256']
 _,_,alltri,valid,usable,tree=n.terrain_index((ROOT/source['manifest']).parent)
 for uid,w in selected:w['native']=np.maximum(w['native'],n.samples(w['points'][:,[0,2]],usable,tree));w['sources'].append(source)
 print(json.dumps({'sheet':source['sheet'],'parts':len(selected)}),flush=True);del alltri,valid,usable,tree;gc.collect()
results=[]
for uid,w in work.items():
 v,c,r,s=w['lengths'];ground=w['native'];rim=w['points'][v+c:v+c+r,1]-ground[v+c:v+c+r];roofs=w['points'][v+c+r:,1]-ground[v+c+r:];tri=w['tri'];indices=np.array(json.loads(gzip.decompress((ROOT/w['spec']['cache']).read_bytes()))['index']).reshape(-1,3);gaps=np.c_[tri[:,:,1]-ground[:v][indices],tri.mean(axis=1)[:,1]-ground[v:v+c]];normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(normals,axis=1)/2;up=normals[:,1]>areas*.5;covered=np.isfinite(gaps).all(axis=1);buried=covered&(gaps<-.5).all(axis=1);bad=np.flatnonzero(buried&up)
 def stats(a):
  finite=a[np.isfinite(a)];return{'samples':len(a),'covered':len(finite),'within2m':int((abs(finite)<=2).sum()),'belowTerrain2m':int((finite< -2).sum()),'aboveTerrain2m':int((finite>2).sum()),'gapRange':[float(finite.min()),float(finite.max())]if len(finite)else None}
 results.append({'uid':uid,'name':parts[uid]['name'],'sourceSHA256':w['spec']['sourceSHA256'],'sources':w['sources'],'currentRim':rows[uid]['rimCounts'],'nativeRim':stats(rim),'nativeProjectedRoof':stats(roofs),'nativeRoofBelowTerrainSamples':int((roofs<-.25).sum()),'triangleSamples':{'triangles':len(tri),'fullyCovered':int(covered.sum()),'area':float(areas.sum()),'fullyBuriedArea':float(areas[buried].sum()),'buriedUpwardTriangles':[{'triangle':int(i),'area':float(areas[i]),'yRange':[float(tri[i,:,1].min()),float(tri[i,:,1].max())],'gapRange':[float(gaps[i].min()),float(gaps[i].max())]}for i in bad]},'rim':[{'position':p['position'],'currentGround':p['ground'],'nativeGround':float(g)if np.isfinite(g)else None}for p,g in zip(rows[uid]['rim'],ground[v+c:v+c+r])],'approval':False})
(DOC/'native-audit.json').write_text(json.dumps({'issue':'HKS-214','rows':results,'method':'Actual runtime Float32 model vertices and triangle centres against retained native terrain TIN with source checksums. Finite geometric tests do not approve subterranean structures or model identity.'},indent=2)+'\n')
for p in results:
 if p['uid']in selection['podiumUids']:print(json.dumps({k:p[k]for k in ['uid','name','nativeRim','nativeProjectedRoof','nativeRoofBelowTerrainSamples']}),flush=True)
