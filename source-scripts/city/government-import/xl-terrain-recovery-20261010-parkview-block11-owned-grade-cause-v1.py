"""Bounded original/literal grade evidence; never physical or root acceptance.

The entire owned finite inventory is retained. Main-body actual finite grade
interfaces are measured despite independent real upward burial and coverage
holes; those negatives cannot be resolved by a wall or carrier exception.
"""
import collections,importlib.util,json,uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
PAIRED=BASE/'government-xl-terrain-recovery-parkview-block11-complete-owned-paired-finite-v1-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1'
BATCH='government-xl-terrain-recovery-parkview-block11-owned-grade-cause-v1-20261010';DOC=BASE/BATCH;UID='landsd/255647:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 for folder in [PHYS,PAIRED,GRAPH]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for f in receipt['evidenceRefs']:assert ref(ROOT/f['path'])==f
 prior=read(PAIRED/'diagnostic.json.gz');r=prior['rows'][0];selection=read(PHYS/'selection.json.gz');source=next(x for x in selection['rows']if x['uid']==UID);asset=ROOT/source['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256'];tri=decode_original_world_triangles(raw)
 geometry=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';rt=next(x for x in read(geometry)['rows']if x['uid']==UID);world=np.asarray(rt['position'],float).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert len(tri)==len(world)==len(r['allFaces'])==10679 and digest(tri.tobytes())==r['completeOriginalWorldSHA256']and digest(world.tobytes())==r['completeActualRenderedWorldSHA256']and digest(ground.tobytes())==r['completeGroundSHA256']
 g=read(GRAPH/'diagnostic.json.gz');parts={f-63133:i for i,p in enumerate(g['components'])if p['actorUID']==UID for f in p['globalOriginalFaces']};assert set(parts)==set(range(10679));mainids=sorted(f for f,i in parts.items()if i==285);assert len(mainids)==2335
 refs=[ref(p)for p in [Path(__file__),PHYS/'selection.json.gz',PAIRED/'diagnostic.json.gz',GRAPH/'diagnostic.json.gz',geometry,asset,*[f/'result.json'for f in [PHYS,PAIRED,GRAPH]],HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']]
 claim=reservations.claim('parkview-owned-grade-cause-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  modes=[]
  for mode,t,key,proofkey in [('original',tri,'unprovedOriginalFaces','pairedExactOriginalFiniteBound'),('literal',world,'unprovedActualRenderedFaces','pairedExactActualRenderedFiniteBound')]:
   n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(n,axis=1);ny=np.divide(n[:,1],length,out=np.zeros(len(length)),where=length>0);negative=[]
   for i in r[key]:
    f=r['allFaces'][i][proofkey];covered=f['groundProjectionCovered']is True;gap=Fraction(f['exactCertifiedLowerClearanceM'])if f['exactCertifiedLowerClearanceM']is not None else None
    negative.append(dict(sourceFace=i,completeOriginalComponent=parts[i],normalYRatio=float(ny[i]),category='non-rendering'if length[i]==0 else 'upward'if ny[i]>.05 else 'downward'if ny[i]<-.05 else 'wall',completeProjectionCovered=covered,exactMinimumGapM=str(gap)if gap is not None else None,coveredClearanceFailure=covered and gap is not None and gap<Fraction(-1,2),originalFace=t[i].tolist()))
   assert len(negative)==320
   interfaces=exact_upper_ground_interfaces(t,mainids,ground);assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)
   modes.append(dict(representation=mode,completeNegativeFaceInventory=negative,counts=dict(categories=dict(collections.Counter(x['category']for x in negative)),projectionGaps=sum(not x['completeProjectionCovered']for x in negative),coveredClearanceFailures=sum(x['coveredClearanceFailure']for x in negative)),completeMainBodyFaces=mainids,completeMainBodyGradeInterfaces=interfaces,genuinePositiveDimensionalGradeWitnesses=len(interfaces),structuralRootCredit=False))
  for f in refs:assert ref(ROOT/f['path'])==f
  result=dict(uid=UID,sourceSHA256=r['sourceSHA256'],completeOwnedFaces=10679,completeOwnedParts=81,frozenCapturedBaselineManifestSHA256=selection['manifestSHA256'],fullOwnedFiniteInventory=ref(PAIRED/'diagnostic.json.gz'),wholeRetainedNativeInventory=prior['wholeRetainedNativeInventoryNotOmitted'],representations=modes,sourceGeometryChanges=0,freshCurrentAcceptance=False,nativeReacceptance=False,fullAcceptance=False,installationApproved=False,gradeRootCredit=False,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('parkview_owned_grade_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'bounded-complete-owned-negative-classification-and-mainbody-finite-grade-cause-v1',[*[ROOT/f['path']for f in refs],DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOwnedFaces=10679,unprovedFacesEachRepresentation=320,gradeWitnessCounts=[x['genuinePositiveDimensionalGradeWitnesses']for x in modes],structuralRootCredit=False,nativeReacceptance=False,fullAcceptance=False));print(json.dumps(dict(counts=[x['counts']for x in modes],gradeWitnessCounts=[x['genuinePositiveDimensionalGradeWitnesses']for x in modes],fullAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
