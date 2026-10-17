"""Exact installed/native patch overlap evidence; no publication approval."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sham-shui-po-pool-';BATCH=PREFIX+'installed-patch-overlap-audit-v1-20261017';DOC=BASE/BATCH
NAMES=['preserved-neighbours-v7-20261017','native-regression-v6-20261017','basic-finite-v4-20261017','basic-ground-capture-v5-20261017','original-group-browser-v6-20261017','native-scope-v1-20261016']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=BASE/(PREFIX+n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert ref(ROOT/p)['sha256']==h,p;refs.append(ROOT/p)
 finite=read(BASE/(PREFIX+NAMES[2])/'summary.json');assert finite['noIntroducedFailures']and len(finite['rows'])==84
 candidate=read(BASE/(PREFIX+NAMES[0])/'terrain-candidates.json')[0];newpath=ROOT/candidate['path'];new=read(newpath);parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
 url='city/data/government-native-313033-0.json';assert sum(e['url']==url for e in manifest['terrainPatches'])==1;oldpath=ROOT/'3d-viewer'/url;old=read(oldpath)
 a,b,c,d=new['coarseCells'];e,f,g,h=old['coarseCells'];cells=[max(a,e),max(b,f),min(c,g),min(d,h)];assert cells==[481,380,482,382]
 pg=parent['meta']['georef'];bounds=[pg['bE']+cells[0]*pg['aE']-834500,816500-(pg['bN']+cells[1]*pg['aN']),pg['bE']+cells[2]*pg['aE']-834500,816500-(pg['bN']+cells[3]*pg['aN'])];region=shapely.box(*bounds)
 surfaces=[]
 for label,patch,path in [('candidate',new,newpath),('retained',old,oldpath)]:
  mesh=patch['nativeMesh'];t=np.asarray(mesh['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];poly=shapely.polygons(t[:,:,[0,2]]);ids=np.flatnonzero(shapely.intersects(poly,region));valid=shapely.area(poly)>1e-10;union=shapely.union_all(poly[valid]);surfaces.append(dict(label=label,source=ref(path),completeFaces=len(t),overlapFaceIds=ids.tolist(),overlapCoveredM2=union.intersection(region).area,overlapUncoveredM2=region.difference(union).area))
 actors=read(BASE/(PREFIX+NAMES[-1])/'complete-bounds.json.gz')['rows'];byuid={r['uid']:r for r in actors};targetrows=[]
 for uid in old['meta']['targetUids']:
  r=byuid[uid];touch=[]
  for lo,hi in r['completeFourWorldBounds']:
   touch.append(shapely.box(lo[0],lo[2],hi[0],hi[2]).intersects(shapely.box(-797.5,-5147.5,-307.5,-4727.5)))
  targetrows.append(dict(uid=uid,completeFourWorldBounds=r['completeFourWorldBounds'],touchesCandidateDomain=any(touch)))
 existing=read(ROOT/'3d-viewer'/candidate['replaces']['url']);assert existing['coarseCells'][3]<=old['coarseCells'][1]
 DOC.mkdir();save(DOC/'overlap-audit.json',dict(candidate=ref(newpath),retained=ref(oldpath),replaced=candidate['replaces'],candidateCells=new['coarseCells'],retainedCells=old['coarseCells'],intersectionCells=cells,intersectionBounds=bounds,intersectionAreaM2=region.area,surfaces=surfaces,retainedTargetActors=targetrows,completeBasicRegressionPassed=True,completeBasicActors=84,retainedPatchWouldRemainByteUnchanged=True,publicationApproved=False,fullAcceptance=False,remaining='Explicit source-bound sibling overlap review/publisher integration must retain full surface and actor obligations; do not bypass the existing publisher rejection.'))
 refs += [newpath,oldpath,parentpath,manifestpath,ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/geo.js',HERE.parent/'island-detail-integration/publish.py']
 out=module('pool_overlap_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-existing-native-patch-overlap-audit-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0','landsd/271043:0']+old['meta']['targetUids'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],overlapCells=cells,retainedTargets=targetrows),flush=True)
if __name__=='__main__':main()
