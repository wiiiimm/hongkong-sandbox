"""Whole original geometry of the three downward-negative bodies, no role.

Closed/outward/self-intersection findings and exact source interfaces cannot
certify a basement, authored footing, load path or current installation.
Body103 alone has independently mapped step context; no inferred function.
"""
from pathlib import Path
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_shell_diagnostic_20261009 import shell_context
from exact_original_shell_intersections_20261009 import shell_self_intersections,rational_face,intersection_points,cross,sub
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-three-downward-bodies-shell-context-v1';DOC=BASE/BATCH
FINITE=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-complete-original-finite-v2';GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1';PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011';BODIES=[41,99,103]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [FINITE,GRAPH,PROBE]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 finite=bound(FINITE,FINITE/'diagnostic.json.gz');graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');s=bound(PROBE,PROBE/'selection.json.gz');r=s['rows'][1];p=ROOT/r['candidate']['path'];assert r['uid']=='landsd/318830:0'and ref(p)['sha256']==r['sourceSHA256'];tri=decode_original_world_triangles(p.read_bytes());refs.append(ref(p));data=finite['rows'][1];assert tri.shape==(5533,3,3)and data['completeOriginalWorldSHA256']==digest(tri.tobytes());ctx=data['completeAllOriginalFacetContexts'];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(tri)),where=length>0)
 downward=[i for i in data['unprovedOriginalFaces']if ratio[i]<-.25];assert len(downward)==14
 owner={i-13841:k for k,c in enumerate(graph['components'])for i in c['globalOriginalFaces']if c['actorUID']==r['uid']};assert sorted({owner[i]for i in downward})==BODIES
 refs.extend(ref(HERE/n)for n in ['exact_packed_world_geometry_20261009.py','original_shell_diagnostic_20261009.py','exact_original_shell_intersections_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']);lo=tri.min(1);hi=tri.max(1);rational={i:rational_face(face)for i,face in enumerate(tri)};zero_ids=[i for i,face in rational.items()if not any(cross(sub(face[1],face[0]),sub(face[2],face[0])))];rows=[]
 for body in BODIES:
  ids=[i-13841 for i in graph['components'][body]['globalOriginalFaces']];shell=shell_context(tri,[ids[0]]);assert shell['componentFaces']==sorted(ids);selfproof=shell_self_intersections(tri[ids]);interfaces=[]
  for i in ids:
   outside=np.flatnonzero(np.all(hi>=lo[i],1)&np.all(lo<=hi[i],1));a=rational_face(tri[i])
   for j in outside:
    j=int(j)
    if j in ids or j in zero_ids:continue
    points=intersection_points(a,rational[j])
    if points:interfaces.append(dict(originalFace=i,otherOriginalPFace=j,exactIntersectionPoints=[[str(v)for v in point]for point in sorted(points)],positiveDimension=len(points)>1,contactIsNotSupportCredit=True))
  rows.append(dict(originalBody=body,completeOriginalPFaceIds=ids,completeOriginalBodyWorldSHA256=digest(tri[ids].tobytes()),sourceBounds=[lo[ids].min(0).tolist(),hi[ids].max(0).tolist()],completeShellContext=shell,completeExactSelfIntersectionProof=selfproof,allActualOriginalPInterfaces=interfaces,completeUpwardFaces=[i for i in ids if ratio[i]>.25],completeDownwardFaces=[i for i in ids if ratio[i]<-.25],completeRawOrdinaryBurialFaces=[i for i in ids if i in data['unprovedOriginalFaces']],completeStrictClearExposedUpwardFaces=[i for i in ids if ratio[i]>.25 and ctx[i]['minimum']['minimumGapM']>0],allBodyFiniteContexts=[ctx[i]for i in ids],sourceFunctionInferred=False,roleAssigned=False,rootOrBridgeCredit=False));print(dict(body=body,closedOutward=shell['closedConsistentlyOriented']and shell['outwardPositiveVolume'],selfIntersectionFree=selfproof['selfIntersectionFree'],originalInterfaces=len(interfaces)),flush=True)
 assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=[r['uid']],rows=rows,completeP5533OriginalWorldSHA256=digest(tri.tobytes()),completeAll5533OriginalPFaceIds=list(range(len(tri))),exactZeroAreaForeignOriginalPFaceIds=zero_ids,zeroAreaForeignFacesRetainedWithoutIntersectionOrSupportCredit=True,all14RawDownwardNegativesPreserved=downward,complete510RawOrdinaryNegativeIds=data['unprovedOriginalFaces'],sourceOnly=True,explicitUndeployedDerivedGroundSHA256=data['completeUndeployedDerivedGroundSHA256'],intentionalBasementOrFootingNotCertified=True,sourceFunctionInferred=False,roleAssigned=False,currentAcceptance=False,rootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze_hoi_three_shells',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'three-whole-original-downward-negative-body-shell-source-interface-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,all14RawDownwardNegativesPreserved=True,roleAssigned=False,rootOrBridgeCredit=False,newlyInstalled=0))
if __name__=='__main__':main()
