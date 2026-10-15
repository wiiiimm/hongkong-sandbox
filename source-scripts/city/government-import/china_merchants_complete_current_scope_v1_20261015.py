"""Nominate the complete current terrain domain; no acceptance from bounds alone."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from complete_actual_native_position_bounds_separation_20261011 import NATIVE_MODES
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-china-merchants-complete-current-scope-v1-20261015';DOC=BASE/BATCH
CENSUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015'
WRAPPER=BASE/'government-xl-china-merchants-current-wrapper-v1-20261015'
def main():
 assert not DOC.exists();r=read(CENSUS/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 paths=[Path(__file__),CENSUS/'result.json',CENSUS/'inventory.json.gz',WRAPPER/'terrain-candidates.json']
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];paths.append(p)
 inv=read(CENSUS/'inventory.json.gz');assert inv['successfullyCapturedActors']==6661 and not inv['errors']
 proposal=read(WRAPPER/'terrain-candidates.json')[0];p=ROOT/proposal['path'];assert digest(p.read_bytes())==proposal['sha256'];paths.append(p);patch=read(p)
 basep=ROOT/'3d-viewer/city/data/terrain.json';paths.append(basep);base=read(basep);g=base['meta']['georef'];origin=base['meta']['origin'];i0,j0,i1,j1=patch['coarseCells']
 coarse=[g['bE']+i0*g['aE']-origin[0],origin[1]-(g['bN']+j0*g['aN']),g['bE']+i1*g['aE']-origin[0],origin[1]-(g['bN']+j1*g['aN'])]
 points=[[coarse[0],coarse[1]],[coarse[2],coarse[3]]]
 def walk(v):
  if 'nativeMesh'in v:
   xyz=np.asarray(v['nativeMesh']['position'],float).reshape(-1,3)
   for a in [xyz,xyz.astype(np.float32).astype(float)]:points.extend(a[:,[0,2]].tolist())
  for c in v.get('patches',[]):walk(c)
 walk(patch);a=np.asarray(points);extent=[*a.min(0),*a.max(0)];extent=[float(x)for x in extent]
 def touches(b):return not(b[2]<extent[0]or b[0]>extent[2]or b[3]<extent[1]or b[1]>extent[3])
 nominated=[];disjoint=[]
 for row in inv['rows']:
  b=[row[f]for f in NATIVE_MODES.values()];union=[min(x[0][0]for x in b),min(x[0][2]for x in b),max(x[1][0]for x in b),max(x[1][2]for x in b)]
  (nominated if touches(union)else disjoint).append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeThreeModeBounds=union))
 manifestp=ROOT/'3d-viewer/city/data/manifest.json';paths.append(manifestp);manifest=read(manifestp);basic=[]
 for t in manifest['tiles']:
  p=ROOT/'3d-viewer'/t['url'];rows=read(p)['buildings'];hits=[]
  for b in rows:
   pts=[v for ring in b.get('rings',[])for v in ring]
   if not pts:continue
   xy=np.asarray(pts);bounds=[*xy.min(0),*xy.max(0)]
   if touches(bounds):hits.append(b)
  if hits:paths.append(p);basic.extend(hits)
 assert len({b['uid']for b in basic})==len(basic)
 DOC.mkdir();save(DOC/'scope.json.gz',dict(coarseCellExtent=coarse,completeParentAndAllChildPackedExtent=extent,currentNativeActors=6661,nominatedNativeActors=nominated,strictlyDisjointNativeActors=disjoint,currentIntersectingForms=basic,fullPhysicalAcceptance=False,publication=False,policy='Whole parent domain and all child literal/Float32 packed positions; touching full originals require complete regression, bounds confer no acceptance.'))
 module('china_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-parent-domain-actor-nomination-v1',paths,dict(uids=['landsd/264206:0'],completeCurrentNativeActors=6661,nominatedNativeUIDs=[x['uid']for x in nominated],intersectingForms=len(basic),fullAcceptance=False))
 print(dict(extent=extent,nativeNominated=len(nominated),nativeDisjoint=len(disjoint),forms=len(basic)),flush=True)
if __name__=='__main__':main()
