"""Prove unchanged MAX surface equations under existing contract, retain node budget hold."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-unchanged-highest-surface-proof-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PRIOR='government-xl-southside-private-terrain-overlap-v1-20261028';UID='landsd/315025:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 prior=take(BASE/PRIOR/'summary.json');assert prior['status']=='unapproved-terrain-overlap-diagnosed'and prior['terrainValidationPassed']is False;patch=take(ROOT/prior['candidate']['path']);overlaps=take(BASE/PRIOR/'positive-area-overlaps.json.gz')['rows'];assert len(overlaps)==prior['completePositiveAreaPairs'];raw=DOC/'unchanged-unapproved-terrain.json';save(raw,patch);m=patch['nativeMesh'];tri=np.asarray(m['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;excess=float(shapely.area(polys[valid]).sum()-shapely.union_all(polys[valid]).area);assert abs(excess-prior['projectedExcessM2'])<1e-6;proofs=[];samples=0;maxerror=0
 for row in overlaps:
  ia,ib=row['faceA'],row['faceB'];poly=shapely.intersection(polys[ia],polys[ib]);points=shapely.get_coordinates(poly);assert len(points)and abs(poly.area-row['projectedAreaM2'])<1e-9;errors=[]
  for fi in [ia,ib]:
   a,b,c=tri[fi];u=b-a;v=c-a;delta=points-a[[0,2]];det=u[0]*v[2]-u[2]*v[0];assert det!=0;s=(delta[:,0]*v[2]-delta[:,1]*v[0])/det;t=(u[0]*delta[:,1]-u[2]*delta[:,0])/det;bary=a[1]+s*u[1]+t*v[1];n=np.cross(u,v);plane=a[1]-(n[0]*delta[:,0]+n[2]*delta[:,1])/n[1];errors.append(float(np.max(abs(bary-plane))));samples+=len(points)
  maxerror=max(maxerror,*errors);proofs.append(dict(faces=[ia,ib],perFaceEquationErrorBoundM=errors,originalInterSurfaceHeightDifferenceM=row['maximumAbsoluteHeightDifferenceM']))
 assert maxerror<.01;sourcefiles=[raw,HERE/'selected_original_terrain_overlap_diagnostic_v1_20261026.py',HERE/'resolve-pass-indexed-parent-clipping.py',ROOT/'3d-viewer/city/data/terrain.json',BASE/PRIOR/'positive-area-overlaps.json.gz']
 for item in patch['meta']['source']['nativeSources']:
  p=ROOT/item['path'];assert ref(p)['sha256']==item['sha256'];sourcefiles.extend(q for q in p.parent.iterdir()if q.suffix in ['.gltf','.bin'])
 sourcefiles=list(dict.fromkeys(sourcefiles));audit=dict(stagedGeometrySha256=ref(raw)['sha256'],nativeProjectedExcessM2=excess,float32HighestRayAgreement=dict(samples=samples,maxError=maxerror,rows=proofs,method='Complete positive-overlap polygon vertices, identical Float32 source facets; independent barycentric/plane affine equations. MAX error is bounded by maximum per-face error. No claim of browser or GPU acceptance.'),source=dict(files=[ref(p)for p in sourcefiles]),qualification='Existing highest-native-surface semantics only. Every overlapping face and height retained; measured inter-surface differences are not declared numerical noise. Per-node runtime budget and full terrain/source/neighbour/browser acceptance remain separate.')
 evidence=DOC/'highest-surface-proof.json';save(evidence,audit);patch['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=excess,evidencePath=ref(evidence)['path'],evidenceSHA256=ref(evidence)['sha256']);parent=read(ROOT/'3d-viewer/city/data/terrain.json');validator=module('southside_existing_native_validator',HERE.parent/'island-detail-integration/native_terrain_validation.py');validator.validate_native_mesh(patch,parent);out=DOC/'height-contract-only-terrain.json.gz';save(out,patch)
 result=dict(uids=[UID],completePositiveOverlapPairs=len(overlaps),unchangedFaces=len(tri),maximumHeightEquationErrorM=maxerror,projectedOverlapM2=excess,existingNativeHeightContractPassed=True,runtimeNodeTriangleBudget=25000,currentNodeFaces=len(tri),runtimeNodeBudgetPassed=len(tri)<=25000,fullTerrainAcceptance=False,sourceGeometryChanges=0,terrainFacetChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Existing source-overlap validator passed with a complete hash-bound highest-surface proof. This is not full terrain acceptance: 76k faces exceed the unchanged 25k per-node runtime budget. A guarded partition preserving all facets and source heights, plus complete current-map acceptance, is still required.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);refs.extend(sourcefiles+[HERE.parent/'island-detail-integration/native_terrain_validation.py']);module('southside_unchanged_highest_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-highest-surface-contract-with-explicit-runtime-budget-hold',refs,result);print(result,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-unchanged-highest-proof-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
