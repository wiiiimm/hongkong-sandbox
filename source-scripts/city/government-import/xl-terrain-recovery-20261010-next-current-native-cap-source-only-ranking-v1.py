"""Bounded source-only next-held shortlist; exact current-native cap contacts.

No identity/support/current-ground acceptance or native reapproval. Old failures
remain; this only prioritises new causal exact-contact investigations.
"""
import json,time
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1';DOC=BASE/BATCH
EXCLUDE={'landsd/89613:0','landsd/88343:0','landsd/246467:0','landsd/320705:0','landsd/254815:0','landsd/79883:0','landsd/89917:0','landsd/58497:0','landsd/63823:0','landsd/121309:0','landsd/148052:0','landsd/266062:0','landsd/75413:0','landsd/101781:0','landsd/268032:0'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';baseline=ref(manifest);installed={};catalogues=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogues.append(ref(path))
  for e in read(path)['models']:assert e['uid']not in installed;installed[e['uid']]=(path,e)
 oldpath=BASE/'government-xl-current-320-blocker-families-20261009/dispositions.json.gz';old=read(oldpath);wanted={r['uid']:r for r in old['rows']if 'terrain-or-foundation'in r['reasonFamilies']and r['uid']not in installed and r['uid']not in EXCLUDE}
 sources={}
 for pattern in ['*/selection.json.gz','*/check-selection.json.gz','*/selection.json','*/check-selection.json']:
  for path in sorted(BASE.glob(pattern)):
   d=read(path)
   for r in d.get('rows',[]):
    uid=r.get('uid');candidate=r.get('candidate')
    if uid not in wanted or not isinstance(candidate,dict)or not candidate.get('path')or r.get('sourceSHA256')!=wanted[uid]['sourceSHA256']:continue
    asset=ROOT/candidate['path']
    if asset.is_file():sources[uid]=(r,path,asset)
 print(json.dumps(dict(remainingTerrainFamily=len(wanted),exactCachedSources=len(sources))),flush=True)
 candidates=[]
 for uid,(row,path,asset) in sources.items():
  bounds=row.get('native',{}).get('model',{}).get('worldBounds')or row.get('candidate',{}).get('entry',{}).get('worldBounds')
  if bounds is None:continue
  bounds=np.asarray(bounds,float)
  possible=[]
  for native,(catalogue,entry)in installed.items():
   n=np.asarray(entry.get('worldBounds'),float)
   if n.shape!=(2,3)or np.any(np.maximum(bounds[0],n[0])>np.minimum(bounds[1],n[1])):continue
   possible.append((native,catalogue,entry))
  if possible:candidates.append((uid,row,path,asset,possible))
 candidates.sort(key=lambda v:(len(v[4]),v[1].get('triangles',10**9),v[0]));rows=[];nativecache={};tested=0
 for uid,row,path,asset,possible in candidates[:24]:
  raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==wanted[uid]['sourceSHA256'];tri=decode_original_world_triangles(raw);contacts=[];testednative=[]
  for native,catalogue,e in possible:
   natasset=catalogue.parent/e['asset'];assert digest(natasset.read_bytes())==e['sha256']
   if native not in nativecache:
    nt=decode_original_world_triangles(natasset.read_bytes());normal=np.cross(nt[:,1]-nt[:,0],nt[:,2]-nt[:,0]);length=np.linalg.norm(normal,axis=1);up=np.flatnonzero((length>0)&(normal[:,1]>.15*length));boxes=shapely.box(nt[up,:,0].min(1),nt[up,:,2].min(1),nt[up,:,0].max(1),nt[up,:,2].max(1));nativecache[native]=(nt,up,shapely.STRtree(boxes))
   nt,up,tree=nativecache[native];testednative.append(dict(uid=native,sourceSHA256=e['sha256'],completeOriginalNativeFaces=len(nt),wholeLandmarkAccepted=e.get('wholeLandmarkAccepted'),asset=ref(natasset),catalogue=ref(catalogue)));found=None
   for i,t in enumerate(tri):
    if not np.any(np.cross(t[1]-t[0],t[2]-t[0])):continue
    for k in tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())):
     j=int(up[k]);u=nt[j]
     if t[:,1].max()<u[:,1].min()or u[:,1].max()<t[:,1].min():continue
     tested+=1;points=intersection_points(rational_face(t),rational_face(u))
     if len(points)>=2:found=dict(nativeUID=native,ownedOriginalFace=i,nativeOriginalUpwardCapFace=j,exactPositiveContactVertices=[[str(v)for v in p]for p in points],ownedOriginalVertices=t.tolist(),nativeOriginalCapVertices=u.tolist());break
    if found:break
   if found:contacts.append(found)
  rows.append(dict(uid=uid,name=row.get('name'),sourceSHA256=row['sourceSHA256'],modelId=row.get('modelId'),completeOriginalFaces=len(tri),cachedSource=ref(asset),cachedSelection=ref(path),historicalReasons=wanted[uid]['reasons'],completeCandidateNativeInventory=testednative,exactOriginalNativeCapContacts=contacts,changedMethodNextStep='Independently qualify the full current source and native cap/root/connected-component paths, source and literal finite terrain, complete current identity/foreign/foundation/runtime/browser gates; preserve every native legacy failure.',fullAcceptance=False))
  save(DOC/'compute-checkpoint.json',dict(rows=rows,sourceOnly=True,newlyInstalled=0,manifestAtSourceProbe=baseline));print(json.dumps(dict(uid=uid,exactPositiveCaps=len(contacts),nativeCandidates=len(possible),tested=len(rows))),flush=True)
 rows.sort(key=lambda r:(not bool(r['exactOriginalNativeCapContacts']),-len(r['exactOriginalNativeCapContacts']),r['completeOriginalFaces'],r['uid']))
 save(DOC/'diagnostic.json.gz',dict(rows=rows,remainingTerrainFamily=len(wanted),exactCachedSources=len(sources),rankedEnvelopeCandidates=len(candidates),boundedCandidatesExamined=len(rows),exactTrianglePairsTested=tested,manifestAtSourceProbe=baseline,manifestAtCompletion=ref(manifest),sourceOnly=True,fullAcceptance=False,nativeReacceptance=False,newlyInstalled=0,sourceGeometryChanges=0,evidenceRefs=[ref(Path(__file__)),ref(oldpath),*catalogues,HERE and ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'exact_original_shell_intersections_20261009.py')]))
 print(json.dumps(dict(positiveCases=[dict(uid=r['uid'],name=r['name'],native=[p['nativeUID']for p in r['exactOriginalNativeCapContacts']])for r in rows if r['exactOriginalNativeCapContacts']],sourceOnly=True)),flush=True)
if __name__=='__main__':main()
