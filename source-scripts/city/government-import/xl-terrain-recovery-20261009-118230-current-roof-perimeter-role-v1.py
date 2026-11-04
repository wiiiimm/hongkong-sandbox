"""Three pinned authored Harbourfront roof footings, existing finite band.

Replays all current independent physical/source/grade/foreign proofs first.
No installation approval: other original parts remain unaccounted.
"""
import collections,hashlib,importlib.util,json,uuid
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_open_roof_perimeter_band_accounting_20261009 import verify,canonical
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-current-roof-perimeter-role-v1';DOC=BASE/BATCH
GRADE=BASE/'xl-terrain-recovery-20261009-118230-current-original-grade-support-v1';GRAPH=BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1';PROVIDER=BASE/'xl-terrain-recovery-20261009-118230-provider-source-inventory-v2'
spec=importlib.util.spec_from_file_location('harbourfront_grade',HERE/'xl-terrain-recovery-20261009-118230-current-original-grade-support-v1.py');grade=importlib.util.module_from_spec(spec);spec.loader.exec_module(grade)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def boundaries(tri,ids,flat):
 edges=collections.Counter(tuple(sorted((tuple(a),tuple(b)))) for i in ids for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)));bottom=float(tri[ids,:,1].min())
 return [[list(v) for v in e] for e,n in sorted(edges.items()) if n==1 and (not flat or e[0][1]==e[1][1]==bottom)]
def recheck():
 raw_grade=grade.recheck();assert json.loads(json.dumps(raw_grade,allow_nan=False))==read(GRADE/'typed-support.json.gz');grade.curb.receipt(GRADE);grade.curb.receipt(PROVIDER)
 physical=grade.curb.PHYSICAL;row=read(physical/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/118230:0' and row['sourceSHA256']=='0e9740f9b9b3061aa4f4bbe26b397db58f870476aa0716745339e505a79c51ff'
 provider=read(PROVIDER/'expected-role.json');assert provider['uid']==row['uid'] and provider['modelId']=='B378291822401063C0' and provider['sourceSHA256']==row['sourceSHA256'] and provider['originalFaceCount']==19438
 raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);assert digest(raw)==row['sourceSHA256'] and digest(tri.tobytes())=='b276304c2b94878d7c47665b7536a1dca385cf0bd52dd8264dff92d7dc9c5863'
 graph=read(GRAPH/'diagnostic.json.gz');components=grade.complete_components(tri,row['uid']);assert components==graph['components'] and len(components)==446 and len(tri)==19438
 ctx=read(grade.curb.CONTEXT)['faces'];role_ids={0:list(range(22)),85:list(range(3912,3936)),333:list(range(11906,12072))+list(range(12792,12840))};roles=[]
 for k,ids in role_ids.items():
  assert components[k]['globalOriginalFaces']==ids
  roles.append(dict(component=k,kind='open-vertical-roof-post' if k!=333 else 'open-bottom-upright-roof-equipment',completeOriginalFaces=ids,completeOriginalLowerBoundary=boundaries(tri,ids,k!=333)))
 independent=raw_grade['resolvedOriginalComponents'];visual=raw_grade['visualOnlyComponents'];assert visual==[422] and len(independent)==298
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeComponentsSHA256=canonical(components),completeCurrentFacetContextsSHA256=canonical(ctx),independentRootedComponentsSHA256=canonical(independent),visualOnlyComponentsSHA256=canonical(visual),sourceRolesSHA256=canonical(roles),providerExteriorOriginalStreamsReceiptSHA256=digest((PROVIDER/'result.json').read_bytes()),currentIndependentGradeReceiptSHA256=digest((GRADE/'result.json').read_bytes()),currentFullPhysicalReceiptSHA256=digest((physical/'result.json').read_bytes()),currentManifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()))
 typed=verify(tri,components,ctx,independent,visual,roles,expected_binding=binding,current_binding=binding)
 geometry=read(grade.curb.GEOMETRY)['rows'][0];world=np.asarray(geometry['position'],float).reshape(-1,3)[np.asarray(geometry['index'],dtype=np.uint32).reshape(-1,3)];assert world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
 # Topology stays authoritative in original source coordinates; actual
 # renderer lower edges must independently stay in the same finite band.
 actual_band=[];roof_ids=typed['completeIndependentlyRootedUpwardRoofFaces']
 for role in roles:
  for edge in role['completeOriginalLowerBoundary']:
   mapped=[]
   for p in edge:
    occurrences=np.argwhere(np.all(tri==p,axis=2));assert len(occurrences)
    positions=np.asarray([world[a,b] for a,b in occurrences]);assert np.all(positions==positions[0]);mapped.append(positions[0])
   proof=verify_contact_segment(np.asarray(mapped),world[roof_ids]);assert proof['verifiedCompleteOriginalEdgeContactBand']
   actual_band.append(dict(component=role['component'],originalEdge=edge,actualRenderedEdge=np.asarray(mapped).tolist(),actualRenderedFixedBandProof=proof))
 excluded=set(visual);adj={k:set() for k in range(446) if k not in excluded}
 for r in raw_grade['ordinaryRootGraphPreserved']['exactOriginalContacts']:
  a,b=r['components']
  if a not in excluded and b not in excluded:adj[a].add(b);adj[b].add(a)
 reached=set(independent)|set(typed['sourceRoofFootingComponents']);todo=list(reached);parents={k:None for k in reached}
 while todo:
  a=todo.pop()
  for b in sorted(adj[a]):
   if b not in reached:reached.add(b);parents[b]=a;todo.append(b)
 unresolved=sorted(set(adj)-reached);assert unresolved==[330,332,417,418,419,420,444]
 refs=raw_grade['evidenceRefs']+[ref(p) for p in [Path(__file__),GRADE/'result.json',GRADE/'typed-support.json.gz',PROVIDER/'result.json',PROVIDER/'expected-role.json',HERE/'original_open_roof_perimeter_band_accounting_20261009.py',HERE/'test_original_open_roof_perimeter_band_accounting_20261009.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'test_exact_original_segment_surface_contact_band_20261009.py']]
 typed.update(uid=row['uid'],sourceSHA256=row['sourceSHA256'],binding=binding,completeSourceProviderRootStreamsReplayed=True,completeCurrentSourceFoundationIdentityForeignGatesReplayed=True,actualRenderedLowerPerimetersWithinSameFixedBand=actual_band,completeOriginalPositiveContactGraphPreserved=True,resolvedOriginalComponents=sorted(reached),unresolvedOriginalComponents=unresolved,originalComponentParents=parents,rawCurrentPhysicalFailuresPreserved=read(physical/'result.json')['reasons'],supportInterfaceAccepted=False,fullAcceptance=False,installationApproved=False,evidenceRefs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']))
 return json.loads(json.dumps(typed,allow_nan=False))
def main():
 assert not DOC.exists();claim=reservations.claim('harbourfront-current-roof-band-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=json.loads(json.dumps(claim['reservation'],default=str))
 try:
  typed=recheck();save(DOC/'typed-role.json.gz',typed)
  spec=importlib.util.spec_from_file_location('current_roof_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.freeze(BATCH,'three-pinned-original-open-roof-footings-within-existing-finite-contact-band-v1',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=[typed['uid']],sourceSHA256=typed['sourceSHA256'],resolvedOriginalComponents=typed['resolvedOriginalComponents'],unresolvedOriginalComponents=typed['unresolvedOriginalComponents'],groundRootCredit=False,exactNoncontactPreserved=True,fullAcceptance=False,installationApproved=False,nextStep='Resolve seven remaining original details independently; then complete staged/runtime/live installation gates.'))
  print(json.dumps(dict(resolved=len(typed['resolvedOriginalComponents']),unresolved=typed['unresolvedOriginalComponents'],fullAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
