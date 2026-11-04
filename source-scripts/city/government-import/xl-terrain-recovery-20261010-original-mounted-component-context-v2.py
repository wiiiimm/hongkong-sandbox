"""Exact source-only mount witnesses for complete unresolved original components.

Every rooted face is tested or rigorously distance-pruned. Neither near distance
nor matching provider metadata grants mount/support acceptance.
"""
import argparse,json,math,importlib.util,uuid
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_distance_20261009 import triangle_distance
from original_shell_diagnostic_20261009 import shell_context
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--historical-manifest');p.add_argument('--support',required=True);p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);p.add_argument('--component',type=int,action='append');a=p.parse_args();doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();support=ROOT/a.support;physical=ROOT/a.physical
 graph=read(support/'diagnostic.json.gz');receipt=read(support/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:
  if r['path']=='3d-viewer/city/data/manifest.json' and ref(ROOT/r['path'])!=r:
   assert a.historical_manifest and digest((ROOT/a.historical_manifest).read_bytes())==r['sha256'],'Exact original manifest archive required'
  else:assert ref(ROOT/r['path'])==r
 selected=read(physical/'selection.json.gz');pieces=[];assets=[]
 for r in selected['rows']:
  asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256'];pieces.append(decode_original_world_triangles(raw));assets.append(asset)
 tri=np.concatenate(pieces);assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 components=graph['components'];rooted=set(graph['resolvedOriginalComponents']);unresolved=set(range(len(components)))-rooted;wanted=sorted(unresolved if a.component is None else set(a.component));assert set(wanted)<=unresolved
 rootids=sorted(i for k in rooted for i in components[k]['globalOriginalFaces']);byface={i:k for k,c in enumerate(components) for i in c['globalOriginalFaces']};lo=tri.min(axis=1);hi=tri.max(axis=1);rootvertices=defaultdict(set)
 for i in rootids:
  for xyz in tri[i]:rootvertices[tuple(xyz)].add(i)
 claim=reservations.claim('original-mount-diagnostic-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  results=[]
  for k in wanted:
   ids=components[k]['globalOriginalFaces'];plo=tri[ids].min(axis=(0,1));phi=tri[ids].max(axis=(0,1));near=[];excluded=[]
   for j in rootids:
    gaps=[max(F(float(plo[d]))-F(float(hi[j,d])),F(float(lo[j,d]))-F(float(phi[d])),F(0)) for d in range(3)];lb=sum(v*v for v in gaps)
    if lb>=1:excluded.append(dict(rootedOriginalFace=j,wholeComponentBBoxLowerSquaredDistanceM2=str(lb)))
    else:near.append(j)
   assert len(near)+len(excluded)==len(rootids);faces=[]
   for i in ids:
    nearest=None;tested=0
    for j in near:
     gaps=[max(F(float(lo[i,d]))-F(float(hi[j,d])),F(float(lo[j,d]))-F(float(hi[i,d])),F(0)) for d in range(3)];lb=sum(v*v for v in gaps)
     if nearest is not None and lb>F(nearest['exactSquaredDistanceM2']):continue
     r=triangle_distance(tri[i],tri[j]);tested+=1
     if nearest is None or F(r['exactSquaredDistanceM2'])<F(nearest['exactSquaredDistanceM2']):nearest=dict(r,rootedSourceFace=j,rootedOriginalComponent=byface[j])
    certified=nearest is not None and F(nearest['exactSquaredDistanceM2'])<1
    faces.append(dict(sourceFace=i,completeOriginalVertices=tri[i].tolist(),nearestCompleteOriginalRootedSurface=nearest,globallyCertifiedAgainstAllRootedOriginalFaces=certified,exactPairsEvaluated=tested,noMountOrSupportCredit=True))
   anchors=[dict(originalVertex=list(xyz),rootedOriginalFaces=sorted(rootvertices[xyz]),rootedOriginalComponents=sorted({byface[i] for i in rootvertices[xyz]})) for xyz in sorted(set(map(tuple,tri[ids].reshape(-1,3)))) if xyz in rootvertices]
   result=dict(component=k,actorUID=components[k]['actorUID'],completeOriginalFaces=ids,wholeBounds=[plo.tolist(),phi.tolist()],shell=shell_context(tri,ids),everyOriginalFaceNearestWitness=faces,exactOriginalAuthoredVertexContacts=anchors,completeRootedOriginalScopeFaces=rootids,rigorouslyExcludedOriginalFaces=excluded,remainingOriginalRootedFaces=near,structuralRootCredit=False,visualRoleAccepted=False)
   results.append(result);save(doc/'partial-diagnostic.json.gz',dict(completeProof=False,results=results,sourceGeometryChanges=0,installationApproved=False));assert reservations.heartbeat(lease)['ok']
   distances=[math.sqrt(float(F(f['nearestCompleteOriginalRootedSurface']['exactSquaredDistanceM2']))) for f in faces if f['nearestCompleteOriginalRootedSurface']]
   print(json.dumps(dict(component=k,faces=len(ids),exactVertexAnchors=len(anchors),minimumFacetDistanceM=min(distances) if distances else None,maximumNearestFacetDistanceM=max(distances) if distances else None)),flush=True)
  refs=([ref(ROOT/a.historical_manifest)] if a.historical_manifest else [])+[ref(q) for q in [Path(__file__),support/'diagnostic.json.gz',support/'result.json',physical/'selection.json.gz',HERE/'exact_original_triangle_distance_20261009.py',HERE/'test_exact_original_triangle_distance_20261009.py',HERE/'original_shell_diagnostic_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]]
  save(doc/'diagnostic.json.gz',dict(uids=[r['uid'] for r in selected['rows']],completeOriginalWorldSHA256=digest(tri.tobytes()),completeRootedOriginalComponents=sorted(rooted),rawAllUnresolvedComponents=sorted(unresolved),requestedCompleteOriginalComponents=wanted,results=results,evidenceRefs=refs,sourceGeometryChanges=0,installationApproved=False,qualification='Exact complete-source distance/topology/vertex-contact diagnosis only. Nearest facet minima do not certify whole-facet contact, visual mounting or structural support. Original unresolved support failures stay explicit.'))
  spec=importlib.util.spec_from_file_location('mount_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-original-mounted-component-geometry-diagnostic-v2',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in selected['rows']],sourceComponentsDiagnosed=len(results),scriptFullAcceptancePassed=False,structuralRootCredit=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
