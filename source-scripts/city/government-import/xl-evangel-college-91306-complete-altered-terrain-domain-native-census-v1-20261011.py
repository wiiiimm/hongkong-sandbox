"""All6645 actual native bounds versus the COMPLETE changed terrain domain.
No geographical recorded-footprint proxy. Every touching/overlapping actor
remains explicitly nominated for complete before/after finite terrain checks.
"""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from complete_actual_native_position_bounds_separation_20261011 import verify,box,strict_planar_separation,NATIVE_MODES,OWNED_MODES
B=ROOT/'docs/astra-city/government-import';CERT=B/'government-xl-evangel-college-91306-all-current6645-native-actual-separation-v1-20261011';PHYS=B/'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'
BATCH='government-xl-evangel-college-91306-complete-altered-terrain-domain-native-census-v1-20261011';DOC=B/BATCH
INVENTORIES=[B/'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011/inventory.json.gz',B/'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011/inventory.json.gz',B/'government-xl-complete-native-actual-position-vancor-post-mount-delta-v1-20261011/inventory.json.gz',B/'government-xl-complete-native-actual-position-evangel-post-elements-delta-v1-20261011/inventory.json.gz']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),manifest];receipts=[]
 for folder in [CERT,PHYS]:
  r=read(folder/'result.json');receipts.append(r)
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for pin in r['evidenceRefs']:p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 sourcecert=read(CERT/'diagnostic.json.gz');physical=read(PHYS/'diagnostic.json.gz');assert sourcecert['currentManifest']==physical['currentManifest']==start
 proof=sourcecert['completeNativeActualBoundsCertificate'];assert proof['completeForeignNativeActors']==6645
 actors=[row for path in INVENTORIES for row in read(path)['rows']];assert len(actors)==len({a['uid']for a in actors})==6645
 oldproof={r['uid']:r for r in proof['rows']};assert set(oldproof)=={a['uid']for a in actors}
 for a in actors:assert oldproof[a['uid']]['completeActualPositionRowSHA256']==canonical(a)
 candidates=read(PHYS/'terrain-candidates.json');assert len(candidates)==1;p=candidates[0];patchpath=ROOT/p['path'];assert ref(patchpath)==dict(path=p['path'],sha256=p['sha256']);patch=read(patchpath)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);g=patch['meta']['georef'];origin=parent['meta']['origin'];x0=g['bE']-origin[0];z0=origin[1]-g['bN'];assert [x0,z0,x0+(patch['w']-1)*g['aE'],z0-(patch['h']-1)*g['aN']]==p['bounds']
 pg=parent['meta']['georef'];i0,j0,i1,j1=patch['coarseCells'];coarse_extent=[pg['bE']+i0*pg['aE']-origin[0],origin[1]-(pg['bN']+j0*pg['aN']),pg['bE']+i1*pg['aE']-origin[0],origin[1]-(pg['bN']+j1*pg['aN'])];assert coarse_extent==p['bounds'];assert read(PHYS/'metrics.json')['inputHashes'][str(parentpath.relative_to(ROOT))]==digest(parentpath.read_bytes());refs.append(parentpath)
 points=np.asarray(patch['nativeMesh']['position'],dtype=np.float32).astype('<f8').reshape(-1,3);assert np.isfinite(points).all()and len(points)>0
 # Include both declared parent-grid replacement extent and EVERY actual packed
 # vertex (unused included). The height coordinate does not affect XZ proof.
 x0,z0,x1,z1=p['bounds'];domain=[[min(x0,float(points[:,0].min())),0,min(z0,float(points[:,2].min()))],[max(x1,float(points[:,0].max())),0,max(z1,float(points[:,2].max()))]];box(domain)
 separated=[];nominated=[]
 for a in actors:
  pairproofs=[];overlaps=[]
  for mode,field in NATIVE_MODES.items():
   box(a[field])
   try:separation=strict_planar_separation(domain,a[field]);pairproofs.append(dict(nativeArithmetic=mode,**separation))
   except AssertionError as error:
    assert str(error)=='Whole actual POSITION bounds overlap or touch; complete finite actor context required';overlaps.append(dict(nativeArithmetic=mode,completeActualUnusedPOSITIONBounds=a[field]))
  record=dict(uid=a['uid'],sourceSHA256=a['sourceSHA256'],completeActualPositionRowSHA256=canonical(a),completePositionVertices=a['completePositionVertices'],strictDomainSeparationProofs=pairproofs)
  if overlaps:nominated.append(dict(**record,overlappingOrTouchingActualBounds=overlaps,fullBeforeAfterFiniteTerrainObligation=True))
  else:separated.append(record)
 assert len(separated)+len(nominated)==6645
 full=None
 if not nominated:full=verify({mode:domain for mode in OWNED_MODES},actors)
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/91306:0'],currentManifest=start,completeChangedTerrainPatch=p,completeDeclaredGridReplacementAndPackedUnusedVertexDomain=domain,completeActualPackedTerrainUnusedVertices=len(points),complete6645CurrentNativeActors=len(actors),strictlyDomainSeparatedActors=separated,terrainDomainNominatedActors=nominated,allActualNativeBoundsDisjointFromCompleteChangedTerrainDomain=not nominated,completeStrictAllWorldCertificate=full,noRecordedGeographicFootprintCredit=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 assert ref(manifest)==start
 for receipt in receipts:
  for pin in receipt['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 refs.extend(INVENTORIES);refs.extend([patchpath,PHYS/'terrain-candidates.json',HERE/'complete_actual_native_position_bounds_separation_20261011.py',HERE/'test_complete_actual_native_position_bounds_separation_20261011.py',DOC/'diagnostic.json.gz'])
 s=importlib.util.spec_from_file_location('evangel_whole_terrain_native_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.freeze(BATCH,'complete-changed-terrain-domain-all6645-current-actual-native-unused-position-census-no-acceptance',refs,dict(uids=['landsd/91306:0'],completeNativeActors=6645,nominatedNativeActors=len(nominated),physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'],nominatedNativeActors=[r['uid']for r in nominated])),flush=True)
if __name__=='__main__':main()
