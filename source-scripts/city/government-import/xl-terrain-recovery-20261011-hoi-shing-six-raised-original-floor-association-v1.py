"""Source-only exact complete floor contact-band leads for six Hoi Shing bodies.

All original faces and previous zero-contact/rim failures remain. Proposed roof
hosts only belong to the source-only derived-ground reachable original podium;
that historical sampled reachability supplies NO current/full-facet host credit.
No geometry, elevation, terrain, root, bridge or accepted-role changes.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_floor_anchor_20261009 import verify_contact
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-six-raised-original-floor-association-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
RIM=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1'
TOPOLOGY=BASE/'government-xl-hoi-shing-unresolved-original-body-topology-v1-20261011'
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
BODIES=[21,22,25,94,95,100];PODIUM='landsd/318830:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];results={}
 for folder in [GRAPH,RIM,TOPOLOGY,PROBE]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  results[folder.name]=receipt;refs.append(ref(folder/'result.json'))
 graph=read(GRAPH/'diagnostic.json.gz');rim=read(RIM/'diagnostic.json.gz');topology=read(TOPOLOGY/'diagnostic.json.gz')
 for folder in [GRAPH,RIM,TOPOLOGY]:assert ref(folder/'diagnostic.json.gz')in results[folder.name]['evidenceRefs'];refs.append(ref(folder/'diagnostic.json.gz'))
 selection=read(PROBE/'selection.json.gz');refs.append(ref(PROBE/'selection.json.gz'));worlds=[]
 for row in selection['rows']:
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];worlds.append(decode_original_world_triangles(asset.read_bytes()));refs.append(ref(asset))
 tri=np.concatenate(worlds);assert tri.shape==(19374,3,3)and digest(tri.tobytes())==graph['binding']['completeOriginalWorldSHA256']==rim['completeOriginalWorldSHA256']==topology['completeOriginalWorldSHA256']
 components=graph['components'];assert len(components)==145 and set(BODIES)<=set(rim['unresolvedSourceBodies'])
 conditional_hosts=[b for b in rim['sourceOnlyDerivedGroundReachedBodies']if components[b]['actorUID']==PODIUM]
 host_faces=sorted(fi for b in conditional_hosts for fi in components[b]['globalOriginalFaces'])
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);roof_faces=[fi for fi in host_faces if normals[fi,1]>0]
 assert roof_faces and not set(BODIES)&set(conditional_hosts);roof=tri[roof_faces]
 refs.extend(ref(HERE/n)for n in ['exact_packed_world_geometry_20261009.py','exact_original_floor_anchor_20261009.py','exact_original_projection_coverage_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('hoi-six-original-floor-association-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 try:
  rows=[]
  for body in BODIES:
   c=components[body];assert c['actorUID']==PODIUM
   topology_row=next(r for r in topology['rows']if r['originalBody']==body);faces=c['globalOriginalFaces'];assert faces==topology_row['completeGlobalOriginalFaces']
   source=tri[faces];bottom=float(source[:,:,1].min());floor_faces=[fi for fi in faces if np.all(tri[fi,:,1]==bottom)and normals[fi,1]<0]
   assert floor_faces,'No complete authored downward global-bottom facets; do not invent a floor'
   proofs=[]
   for fi in floor_faces:
    proof=verify_contact(tri[fi],roof,band=.1);proof['globalOriginalFace']=fi;proof['allOriginalIntersectingHostFaces']=[roof_faces[p['originalGroundFace']]for p in proof['allOriginalIntersectingPlanePieces']];proofs.append(proof)
    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
   rows.append(dict(originalBody=body,completeOriginalFaces=faces,completeOriginalBodySHA256=digest(source.tobytes()),originalLowestYM=bottom,allOriginalGlobalBottomDownwardFaces=floor_faces,completeFloorProofs=proofs,conditionalCompleteFloorWithinExistingContactBand=all(p['verifiedCompleteFacetContactBand']for p in proofs),originalExactContactsAndRimFailuresPreserved=True,sourceOnlyHostReachabilityNotFullHostQualification=True,roleAssigned=False,structuralRootOrBridgeCredit=False))
   print(dict(originalBody=body,originalBottomFaces=len(floor_faces),conditionalAllFloorPositive=rows[-1]['conditionalCompleteFloorWithinExistingContactBand']),flush=True)
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(completeOriginalFaces=19374,completeOriginalWorldSHA256=digest(tri.tobytes()),examinedOriginalBodies=BODIES,sourceOnlyConditionalHostBodies=conditional_hosts,completeOriginalUpwardHostFaces=roof_faces,completeOriginalUpwardHostSHA256=digest(roof.tobytes()),rows=rows,previousDerivedGroundUndeployed=True,sourceOnly=True,currentAcceptance=False,fullHostGroundFiniteGradeCapAndFourStreamQualificationRequired=True,originalGeometryChanges=0,rootOrBridgeCredit=False,roleAssigned=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze_hoi_floors',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'six-original-raised-body-whole-floor-existing-band-conditional-source-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(sourceOnly=True,currentAcceptance=False,examinedBodies=BODIES,conditionalPositiveBodies=[r['originalBody']for r in rows if r['conditionalCompleteFloorWithinExistingContactBand']],originalGeometryChanges=0,rootOrBridgeCredit=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
