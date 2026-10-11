"""Complete original bottom-edge contact bands on already rooted original roofs.

Geometric diagnostic only. Does not invent omitted bases, claim structural
roots, move source parts, ignore any component or permit installation.
"""
import importlib.util,json,uuid,collections
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-original-roof-perimeters-v1';DOC=BASE/BATCH
GRADE=BASE/'xl-terrain-recovery-20261009-118230-current-original-grade-support-v1';GRAPH=BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1'
PHYSICAL=BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009';CONTEXT=BASE/'xl-terrain-recovery-20261009-118230-boundary-current-complete-context-v3/diagnostic.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def receipt(p):
 r=read(p/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for item in r['evidenceRefs']:assert ref(ROOT/item['path'])==item
 return r
def main():
 assert not DOC.exists();claim=reservations.claim('harbourfront-roof-perimeter-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=json.loads(json.dumps(claim['reservation'],default=str))
 try:
  gr=receipt(GRADE);sr=receipt(GRAPH);grade=read(GRADE/'typed-support.json.gz');graph=read(GRAPH/'diagnostic.json.gz');source=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/source['candidate']['path'];tri=decode_original_world_triangles(asset.read_bytes());assert digest(asset.read_bytes())==source['sourceSHA256']==grade['sourceSHA256'];assert digest(tri.tobytes())==grade['binding']['completeOriginalWorldTrianglesSHA256'];ctx=read(CONTEXT)['faces'];assert len(ctx)==len(tri)==19438
  rooted=grade['resolvedOriginalComponents'];rootscope=sorted(i for k in rooted for i in graph['components'][k]['globalOriginalFaces']);n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(n)),where=length>0);roof_ids=[i for i in rootscope if ratio[i]>.25 and ctx[i]['minimum']['minimumGapM']>=-.5];roofs=tri[roof_ids];assert len(roofs)
  rows=[]
  for k in grade['unresolvedOriginalComponents']:
   ids=graph['components'][k]['globalOriginalFaces'];part=tri[ids];bottom=float(part[:,:,1].min());edges=collections.defaultdict(list)
   for i in ids:
    for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
     if a[1]==b[1]==bottom and tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
   results=[];boundary_adj=collections.defaultdict(set)
   for edge,members in sorted(edges.items()):
    a,b=edge;band=verify_contact_segment(np.asarray(edge),roofs);band['completeOriginalSurfacePieces']=[{**r,'originalSourceFace':roof_ids[r['originalSurfaceFace']]} for r in band['completeOriginalSurfacePieces']];results.append(dict(exactOriginalEdgeSourceFaces=members,originalLowerEdge=edge,band=band));boundary_adj[a].add(b);boundary_adj[b].add(a)
   closed=bool(boundary_adj) and all(len(v)==2 for v in boundary_adj.values());components=0;remaining=set(boundary_adj)
   while remaining:
    seen={min(remaining)};todo=list(seen)
    while todo:
     for j in boundary_adj[todo.pop()]:
      if j not in seen:seen.add(j);todo.append(j)
    remaining-=seen;components+=1
   rows.append(dict(component=k,completeOriginalFaces=ids,completeOriginalBounds=graph['components'][k]['bounds'],minimumOriginalElevationM=bottom,allOriginalMinimumEdges=results,allOriginalMinimumEdgesWithinExistingStrictRoofBand=bool(results) and all(r['band']['verifiedCompleteOriginalEdgeContactBand'] for r in results),exactLowerEdgeClosedLoops=components if closed else None,lowerEdgeVertexDegrees={str(p):len(v) for p,v in boundary_adj.items()},flatMinimumFaceCount=sum(bool(np.all(tri[i,:,1]==bottom)) for i in ids),structuralRootCredit=False,installationApproved=False))
   assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(component=k,lowerEdges=len(results),wholeBand=rows[-1]['allOriginalMinimumEdgesWithinExistingStrictRoofBand'],lowerClosedLoops=rows[-1]['exactLowerEdgeClosedLoops'])),flush=True)
  refs=[ref(p) for p in [Path(__file__),asset,PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',CONTEXT,GRADE/'result.json',GRADE/'typed-support.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'test_exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
  result=dict(uid=source['uid'],sourceSHA256=source['sourceSHA256'],completeOriginalWorldSHA256=digest(tri.tobytes()),currentSourceGroundRootReceipt=ref(GRADE/'result.json'),independentlyRootedOriginalComponents=rooted,completeStrictRootedOriginalRoofFaces=roof_ids,completeRootedOriginalRoofTrianglesSHA256=digest(roofs.tobytes()),allRemainingOriginalComponents=rows,remainingCount=len(rows),candidateWholePerimeterBandComponents=[r['component'] for r in rows if r['allOriginalMinimumEdgesWithinExistingStrictRoofBand'] and r['exactLowerEdgeClosedLoops']],rawExactNoContactFailuresPreserved=True,structuralRootCredit=False,fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('roof_perimeter_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.freeze(BATCH,'original-complete-lower-perimeter-rooted-roof-fixed-contact-band-diagnostic-v1',[ROOT/r['path'] for r in refs],dict(uids=[source['uid']],sourceSHA256=source['sourceSHA256'],completeRemainingComponents=len(rows),candidateWholePerimeterBandComponents=result['candidateWholePerimeterBandComponents'],structuralRootCredit=False,fullAcceptance=False,installationApproved=False,nextStep='Bind source-specific footing/exterior semantics and all current source/component/foreign/runtime proofs before any support credit; unresolved source parts remain held.'))
  print(json.dumps(dict(remaining=len(rows),candidates=result['candidateWholePerimeterBandComponents'],structuralRootCredit=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
