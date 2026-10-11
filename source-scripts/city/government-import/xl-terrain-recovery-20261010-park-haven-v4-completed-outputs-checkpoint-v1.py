"""Fence completed source/terrain outputs after an interrupted receipt writer.

No physical acceptance is inferred from process completion. All saved complete
numeric/current/source input hashes and independent gate results are replayed;
the original interruption and unresolved tower support remain explicit.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BATCH='government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/246467:0','landsd/320705:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not (DOC/'result.json').exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);selection=read(DOC/'selection.json.gz');assert selection['manifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()) and [r['uid'] for r in selection['rows']]==UIDS
 geometry=read(LOCAL/'runtime-geometry.json.gz');metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');foundation=read(DOC/'foundation.json');native=read(DOC/'native-neighbour-checks.json');neighbours=read(DOC/'neighbour-checks.json');inputs=read(DOC/'neighbour-inputs.json.gz');contexts=read(LOCAL/'frozen-inputs/context.json.gz')['rows']
 for d in [geometry,metrics,native,inputs]:
  for path,sha in (d.get('inputHashes') or d.get('hashes') or {}).items():assert digest((ROOT/path).read_bytes())==sha
 assets=[]
 for row in selection['rows']:
  asset=ROOT/row['candidate']['path'];assets.append(asset);assert digest(asset.read_bytes())==row['sourceSHA256'];r=next(r for r in geometry['rows'] if r['uid']==row['uid']);world=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index'],np.uint32).reshape(-1,3)];tri=decode_original_world_triangles(asset.read_bytes());assert tri.shape==world.shape and np.max(np.abs(tri-world))<=1e-9 and len(tri)==row['native']['model']['triangles']
  proof=verify_files(row,next(c for c in contexts if c['uid']==row['uid']),LOCAL/'receipt-recovery-identity'/row['uid'].split('/')[1]);assert proof['passed'] and proof==next(r for r in read(DOC/'owned-source-identity.json')['rows'] if r['uid']==row['uid'])
  m=next(r for r in metrics['rows'] if r['uid']==row['uid']);f=next(r for r in foundation['rows'] if r['uid']==row['uid']);assert m['sourcePreserved'] and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004 and f['strictFoundationAccepted'] is True and f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==len(tri) and f['foundation']['fullyBuriedUpwardTriangles']==f['foundation']['fullyBuriedTriangles']==0
 assert validation['checksPassed']==validation['loaderAccepted']==2 and validation['exceptions']==0 and native['blocked']==native['resolved']==['landsd/246270:0'] and all(r['passed'] is True for r in native['rows']);assert len(neighbours['rows'])==len(inputs['rows'])==24 and all(not r['reasons'] or (r['uid']=='landsd/246270:0' and r['reasons']==['existing-native-neighbour-requires-full-mesh-check']) for r in neighbours['rows'])
 s=importlib.util.spec_from_file_location('policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(s);s.loader.exec_module(policy)
 from terrain_diagnostic_resolution import resolve_global_bottom_warning
 reasons=[];decisions=[]
 for row in selection['rows']:
  uid=row['uid'];m=next(r for r in metrics['rows'] if r['uid']==uid);f=next(r for r in foundation['rows'] if r['uid']==uid);identity=next(r for r in read(DOC/'owned-source-identity.json')['rows'] if r['uid']==uid);raw=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['proof']),m,metrics['profiles']['mobile']);d=resolve_global_bottom_warning(next(v for v in validation['results'] if v['uid']==uid),m,f);reasons.extend(uid+':'+r for r in [*raw,*d['remaining']]);decisions.append(dict(uid=uid,numericReasons=raw,diagnosticResolution=d))
 save(DOC/'physical-decisions-recovery.json',dict(rows=decisions));save(DOC/'interrupted-before-receipt.json',dict(exitCode=143,allCompletePhysicalOutputsPresent=True,originalRunnerCompletedTerrainAndNumericGates=True,originalRunnerHadNoNeonJobAtInterruption=True,receiptWriterRecoveredWithoutRepeatingTerrain=True,installationApproved=False))
 paths=[Path(__file__),HERE/'xl-terrain-recovery-20261010-park-haven-retained-original-pair-physical-v4.py',HERE/'xl-terrain-recovery-20261010-park-haven-retained-original-pair-contact-v4.py',LOCAL/'runtime-geometry.json.gz',LOCAL/'frozen-inputs/check-selection.json.gz',LOCAL/'frozen-inputs/context.json.gz',HERE/'acceptance-policy.py',HERE/'terrain_diagnostic_resolution.py',HERE/'exact_original_georef_cell_identity_20261009.py',*assets]
 for d in [geometry,metrics,native,inputs]:paths.extend(ROOT/p for p in (d.get('inputHashes') or d.get('hashes') or {}))
 for c in read(DOC/'terrain-candidates.json'):assert ref(ROOT/c['path'])=={k:c[k] for k in ['path','sha256']};paths.append(ROOT/c['path'])
 spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);assert reservations.owns(lease)
 f.freeze(BATCH,'completed-whole-physical-outputs-after-interrupted-writer-v1',paths,dict(uids=UIDS,sourceSHA256s={r['uid']:r['sourceSHA256'] for r in selection['rows']},reasons=sorted(set(reasons)),scriptChecksPassed=not reasons,allCurrentNeighbourForms=24,currentNativeOriginal246270Passed=True,fullSourceFoundationsPassed=True,sourceGeometryChanges=0,terrainProposalGeometryChanged=True,disjointProjectionProtectionAccepted=False,currentAcceptancePassed=False,fullAcceptance=False,interruptedExitCode=143,independentSourceSupportAndFullFacetProofStillRequired=True));assert reservations.release(lease)['ok'];print(dict(fenced=True,reasons=sorted(set(reasons))),flush=True)
if __name__=='__main__':main()
