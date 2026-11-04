"""Exact current binding of independently fenced King Cheung complete proofs.

All mathematical source/contact/finite captures are reused only under unchanged
whole source/world/current inputs. No blanket geometry or current-role waiver.
"""
import copy,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from king_cheung_whole_current_role_policy_v2_20261011 import compose,UID,SOURCE
BASE=ROOT/'docs/astra-city/government-import'
DOCS=dict(placement=BASE/'government-xl-king-cheung-95691-fourteen-source-visual-context-v2-20261011',identity=BASE/'government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011',
 input=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011',
 finite=BASE/'government-xl-king-cheung-95691-complete18742-current-finite-diagnostic-v1-20261011',
 graph=BASE/'government-xl-king-cheung-95691-complete908-source-component-interfaces-v2-20261011',
 foundation=BASE/'government-xl-king-cheung-95691-current-foundation-skin-role-proposal-v2-20261011',
 canopy=BASE/'government-xl-king-cheung-95691-current-canopy-post-role-proposal-v1-20261011',
 mounts=BASE/'government-xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v2-20261011',
 physical=BASE/'government-xl-king-cheung-95691-unchanged-current-ordinary-physical-v1-20261011',
 native=BASE/'government-xl-king-cheung-95691-all-current6642-native-actual-separation-v1-20261011',
 foreign=BASE/'government-xl-king-cheung-95691-complete-current-four-foreign-basic-context-v1-20261011')
MANIFEST_SHA='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def receipt_pins(receipt,cache=None):
 cache={}if cache is None else cache
 for pin in receipt['evidenceRefs']:
  assert set(pin)=={'path','sha256'}
  key=(pin['path'],pin['sha256'])
  if key not in cache:assert ref(ROOT/pin['path'])==pin;cache[key]=True
 return cache
def verify_files():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA
 current_manifest=ref(manifest);receipts={};cache={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for label,folder in DOCS.items():
   receipt=read(folder/'result.json');assert receipt['newlyInstalled']==0
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   cache=receipt_pins(receipt,cache);receipts[label]=receipt
  assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(UID,)).fetchone()
  selection=read(DOCS['identity']/'selection.json.gz');assert selection['manifestSHA256']==MANIFEST_SHA and len(selection['rows'])==1
  row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE and row['triangles']==18742
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 capture=read(DOCS['input']/'complete-current-actual-source-and-ground.json.gz');data=read(DOCS['input']/'complete-four-stream-ground-inputs.json.gz')
 for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCE
 original=decode_original_world_triangles(asset.read_bytes());assert original.shape==(18742,3,3)
 assert np.array_equal(original,np.asarray(data['completeWorldStreams']['providerOriginal']['completeWorldTriangles']))
 catalogue_refs=[ref(ROOT/'3d-viewer'/u)for u in json.loads(before)['officialModelCatalogues']];assert len(catalogue_refs)==213
 assert catalogue_refs==capture['completeCurrentCatalogueRefs']
 entries=[e for pin in catalogue_refs for e in read(ROOT/pin['path'])['models']];assert len(entries)==len({e['uid']for e in entries})==6642 and UID not in {e['uid']for e in entries}
 runtime=read(HERE/'local'/DOCS['physical'].name/'runtime-geometry.json.gz')['rows'];assert len(runtime)==1 and runtime[0]['uid']==UID and runtime[0]['sourceSHA256']==SOURCE
 r=runtime[0];actual=np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 assert np.array_equal(actual,np.asarray(data['completeWorldStreams']['actualLiteral']['completeWorldTriangles'])) and np.array_equal(ground,np.asarray(data['completeDrawnGround']))
 identity=read(DOCS['identity']/'identity.json');assert identity==read(DOCS['physical']/'identity.json')
 documents={k:read(p/('proposal.json.gz'if k in ['foundation','canopy']else'diagnostic.json.gz'))for k,p in DOCS.items()if k not in ['identity','input']}
 role=compose(data=data,identity=identity,current_manifest=current_manifest,**documents)
 # Bind complete actual/current byte tuples; unchanged prior calculations are
 # evidence, never a blanket old-global-manifest allowance.
 role.update(exactWholeCurrentInputsUnchanged=True,completeCurrentCatalogueRefs=catalogue_refs,
  independentCompletedProofJobs={k:r['jobId']for k,r in receipts.items()},
  completeCurrentInputHashes=capture['inputHashes'],actualLiteralEqualsProductionRuntimeExactly=True,
  actualFourFacetGroundEqualsProductionRuntimeExactly=True,mathematicalProofsReusedOnlyForIdenticalWholeInputs=True)
 entry=copy.deepcopy(row['candidate']['entry']);assert entry['uid']==UID and entry['sha256']==SOURCE and not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
 entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,
  sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[],
  placementReview='Complete unchanged King Cheung original18742 facets and908 real source components retained.714 components have actual positive-dimensional source connections to the genuine original262-face perimeter foundation skin and independently clear mainbody23. The wholly buried original lower leaf799 remains a source-backed foundation surface and supplies no exposed bridge. The104 original ancillary entrance canopy/post faces retain full source ownership and their independent actual-grade/clear-cap/open-post-skin proofs.177 complete authored visual details have every original opening boundary associated to the qualified envelope within the existing finite .1m band. Four original open-bottom roof boxes and ten repeated lower facade ledges or trims have a separately reviewed source placement interpretation, preserving all fourteen prior full-boundary distance failures. All191 are nonstructural visual surfaces and supply no roots or bridges; no mechanical function or mount certified for the14 named placement parts. One original zero-area face1149 remains in finite/runtime/rendered source inventory with no graph credit. All four source/arithmetic streams, whole foundation/runtime and every current four BASIC/6642 native foreign actor remain independently checked. Source attributes/root/poses and current terrain are unchanged; no legal ownership, closed-solid or load-bearing claims.')
 assert manifest.read_bytes()==before
 for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 return role,entry
