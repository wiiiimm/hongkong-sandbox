"""Source-only complete original edge/facet mount witnesses, no role credit."""
import importlib.util,json,uuid
from fractions import Fraction as F
from pathlib import Path
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_source_surface_contact_band_20261009 import verify_contact
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';SUPPORT=BASE/'xl-terrain-recovery-20261010-glorious-peak-wall-grade-source-v1';NEAREST=BASE/'xl-terrain-recovery-20261010-glorious-peak-mounted-original-context-v1';PHYSICAL=BASE/'government-xl-terrain-recovery-glorious-peak-original-pair-current-physical-v2-20261010';BATCH='xl-terrain-recovery-20261010-glorious-peak-finite-original-mounts-v1';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();graph=read(SUPPORT/'diagnostic.json.gz');nearest=read(NEAREST/'diagnostic.json.gz');rows=read(PHYSICAL/'selection.json.gz')['rows'];assets=[ROOT/r['candidate']['path'] for r in rows];assert all(digest(p.read_bytes())==r['sourceSHA256'] for p,r in zip(assets,rows));tri=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lo=tri.min(axis=1);hi=tri.max(axis=1);rooted=set(graph['resolvedOriginalComponents']);results=[]
 for d in [SUPPORT,NEAREST]:
  rr=read(d/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(rr['jobId'],)).fetchone()==('complete',rr)
 claim=reservations.claim('glorious-finite-mounts-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for part in nearest['results']:
   k=part['component'];ids=graph['components'][k]['globalOriginalFaces'];hostcomps=sorted({f['nearestCompleteOriginalRootedSurface']['rootedOriginalComponent'] for f in part['everyOriginalFaceNearestWitness']});assert set(hostcomps)<=rooted and k not in rooted;hosts=sorted(i for c in hostcomps for i in graph['components'][c]['globalOriginalFaces']);assert all(graph['components'][c]['actorUID']==part['actorUID'] for c in hostcomps)
   plo=tri[ids].min(axis=(0,1));phi=tri[ids].max(axis=(0,1));near=[];excluded=[]
   for j in hosts:
    ds=[max(F(float(plo[z]))-F(float(hi[j,z])),F(float(lo[j,z]))-F(float(phi[z])),F(0)) for z in range(3)];lb=sum(x*x for x in ds)
    if lb>F(.1)**2:excluded.append(dict(originalRootedHostFace=j,exactWholeComponentLowerSquaredDistance=str(lb)))
    else:near.append(j)
   edgeinc=defaultdict(list)
   for i in ids:
    vs=list(map(tuple,tri[i]))
    for a,b in zip(vs,vs[1:]+vs[:1]):edgeinc[tuple(sorted((a,b)))].append((i,a,b))
   boundary=[v[0] for v in edgeinc.values() if len(v)==1];facets=[];edges=[]
   for axis in range(3):
    perm=[z for z in range(3) if z!=axis];perm=[perm[0],axis,perm[1]];surfaces=[j for j in near if n[j,axis]!=0];ground=tri[surfaces][:,:,perm]
    if not surfaces:continue
    for i in ids:
     if n[i,axis]==0:continue
     band=verify_contact(tri[i][:,perm],ground)
     if band['verifiedCompleteFacetContactBand']:facets.append(dict(sourceFace=i,axis=axis,signedCoordinatePermutation=perm,completeHostFaces=surfaces,band=band))
    for i,a,b in boundary:
     band=verify_contact_segment(np.asarray([a,b])[:,perm],ground)
     if band['verifiedCompleteOriginalEdgeContactBand']:edges.append(dict(sourceFace=i,edge=[list(a),list(b)],axis=axis,coordinatePermutation=perm,completeHostFaces=surfaces,band=band))
   results.append(dict(component=k,actorUID=part['actorUID'],completeOriginalFaces=ids,independentlyRootedHostComponents=hostcomps,completeHostSourceFaces=hosts,rigorouslyDisjointOutsideFixedBandFaces=excluded,allBoundaryEdges=[dict(sourceFace=i,edge=[list(a),list(b)]) for i,a,b in boundary],verifiedCompleteOriginalFacetBands=facets,verifiedCompleteOriginalBoundaryBands=edges,visualRoleAccepted=False,structuralRootCredit=False));save(DOC/'partial-diagnostic.json.gz',results);assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(component=k,completeFacetMounts=len(facets),completeBoundaryMounts=len(edges))),flush=True)
  refs=[ref(q) for q in [Path(__file__),SUPPORT/'result.json',SUPPORT/'diagnostic.json.gz',NEAREST/'result.json',NEAREST/'diagnostic.json.gz',PHYSICAL/'selection.json.gz',HERE/'exact_original_source_surface_contact_band_20261009.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',*assets]];save(DOC/'diagnostic.json.gz',dict(uids=[r['uid'] for r in rows],results=results,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False,evidenceRefs=refs));spec=importlib.util.spec_from_file_location('glorious_mount_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-original-finite-facet-edge-visual-mount-diagnostic-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in rows],componentsDiagnosed=len(results),visualRoleAccepted=False,structuralRootCredit=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
