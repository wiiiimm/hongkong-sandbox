"""Bounded original/literal cap and all-owned path diagnostic for Parkview11.

No native reacceptance/root credit. Carrier170 ground support remains independent;
all complete coarse native/owned negatives retained while paired math continues.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_20261010 import verify
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1'
COARSE=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-and-literal-finite-v1'
BATCH='government-xl-terrain-recovery-parkview-block11-bounded-original-literal-carrier-lead-v1-20261010';DOC=BASE/BATCH
UIDS=['landsd/254491:0','landsd/255647:0'];CARRIER=170;CAP=57951

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def receipt(folder):
 r=read(folder/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for f in r['evidenceRefs']:assert ref(ROOT/f['path'])==f
 return r

def main():
 assert not DOC.exists()
 for p in [PHYS,GRAPH,COARSE]:receipt(p)
 selection=read(PHYS/'selection.json.gz');geometry=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';rt=read(geometry);g=read(GRAPH/'diagnostic.json.gz');coarse=read(COARSE/'diagnostic.json.gz');tri=[];actual=[];ground=[];assets=[]
 for uid in UIDS:
  row=next(r for r in selection['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];assets.append(asset);t=decode_original_world_triangles(raw);r=next(r for r in rt['rows']if r['uid']==uid);w=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];s=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);old=next(x for x in coarse['rows']if x['uid']==uid);assert digest(t.tobytes())==old['completeOriginalWorldSHA256']and digest(w.tobytes())==old['completeActualRenderedWorldSHA256']and digest(s.tobytes())==old['completeGroundSHA256'];tri.append(t);actual.append(w);ground.append(s)
 source=np.concatenate(tri);literal=np.concatenate(actual);assert digest(source.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'] and len(source)==73812 and len(g['components'])==366
 components=g['components'];owned={i for i,c in enumerate(components)if c['actorUID']==UIDS[1]};assert len(owned)==81 and components[CARRIER]['actorUID']==UIDS[0]and CAP in components[CARRIER]['globalOriginalFaces']
 cap=[]
 for name,world in [('completeOriginal',source),('actualRendered',literal)]:
  n=np.cross(world[CAP,1]-world[CAP,0],world[CAP,2]-world[CAP,0]);normalYRatio=float(n[1]/np.linalg.norm(n));assert normalYRatio>.15
  proof=verify(world[CAP],ground[0]);cap.append(dict(representation=name,sourceFace=CAP,normalYRatio=normalYRatio,completeFiniteProof=proof,strictlyExposed=proof['groundProjectionCovered']is True and float(__import__('fractions').Fraction(proof['exactCertifiedLowerClearanceM']))>0))
 allowed=owned|{CARRIER};adj={i:set()for i in allowed};by_pair={}
 for c in g['contactWitnesses']:
  a,b=c['components']
  if a in allowed and b in allowed:adj[a].add(b);adj[b].add(a);by_pair[tuple(sorted([a,b]))]=c
 parents={CARRIER:None};queue=[CARRIER]
 while queue:
  a=queue.pop(0)
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;queue.append(b)
 contacts=[];caps=set()
 for child,parent in sorted(parents.items()):
  if parent is None:continue
  c=by_pair[tuple(sorted([child,parent]))];ids=c['globalOriginalFaces'];points=intersection_points(rational_face(source[ids[0]]),rational_face(source[ids[1]]));actualpoints=intersection_points(rational_face(literal[ids[0]]),rational_face(literal[ids[1]]));source_dimension=contact_measure(points)['dimension']if points else -1;literal_dimension=contact_measure(actualpoints)['dimension']if actualpoints else -1
  if CARRIER in c['components']:caps.add(ids[c['components'].index(CARRIER)])
  contacts.append(dict(parent=parent,child=child,globalOriginalFaces=ids,sourceDimension=source_dimension,literalDimension=literal_dimension,sourcePositiveDimensional=source_dimension>0,literalPositiveDimensional=literal_dimension>0,sourcePoints=[[str(v)for v in p]for p in points],literalPoints=[[str(v)for v in p]for p in actualpoints]))
 refs=[ref(p)for p in [Path(__file__),PHYS/'selection.json.gz',geometry,GRAPH/'diagnostic.json.gz',COARSE/'diagnostic.json.gz',*[x/'result.json'for x in [PHYS,GRAPH,COARSE]],*assets,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']]
 r=dict(uids=UIDS,frozenCapturedBaselineManifestSHA256=selection['manifestSHA256'],completeOriginalFaces=73812,completeOriginalComponents=366,ownedComponents=sorted(owned),nativeCarrierComponent=CARRIER,nativeCarrierCompleteOriginalFaces=len(components[CARRIER]['globalOriginalFaces']),nativeCarrierOriginalBounds=components[CARRIER]['bounds'],nativeCarrierRawOrdinaryRootProof=next(x for x in g['ordinaryRootProofs']if x['component']==CARRIER),nativeCarrierRootCreditGranted=False,fullNativeReacceptance=False,nativeReacceptance=False,completeOriginalAndLiteralCapContext=cap,capStrictlyExposedInBothRepresentations=all(c['strictlyExposed']for c in cap),completeSourceAndLiteralOwnedContactPaths=contacts,allOwnedReachedFromCarrierAsUnrootedGraph=owned<=set(parents),allCreditedContactCandidatesPositiveInBothRepresentations=all(c['sourcePositiveDimensional']and c['literalPositiveDimensional']for c in contacts),allCarrierInterfaceFaces=sorted(caps),wholeLegacyCoarseNativeNegativesPreserved=next(x['unprovedOriginalFaceBounds']for x in coarse['rows']if x['uid']==UIDS[0]),wholeOwnedCoarseNegativesPreserved=next(x['unprovedOriginalFaceBounds']for x in coarse['rows']if x['uid']==UIDS[1]),sourceGeometryChanges=0,freshCurrentAcceptance=False,fullAcceptance=False,installationApproved=False,evidenceRefs=refs)
 for f in refs:assert ref(ROOT/f['path'])==f
 save(DOC/'diagnostic.json.gz',r);s=importlib.util.spec_from_file_location('bounded_parkview_lead_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'bounded-complete-original-literal-current-carrier-cap-and-owned-path-lead-v1',[ROOT/x['path']for x in refs],dict(uids=UIDS,completeOwnedComponents=81,capStrictlyExposedInBothRepresentations=r['capStrictlyExposedInBothRepresentations'],allOwnedReachedFromUnrootedCarrier=r['allOwnedReachedFromCarrierAsUnrootedGraph'],carrierRootCreditGranted=False,nativeReacceptance=False,fullAcceptance=False));print(json.dumps({k:r[k]for k in ['capStrictlyExposedInBothRepresentations','allOwnedReachedFromCarrierAsUnrootedGraph','allCreditedContactCandidatesPositiveInBothRepresentations','allCarrierInterfaceFaces']}),flush=True)
if __name__=='__main__':main()
