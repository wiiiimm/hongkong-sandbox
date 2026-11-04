"""Persist completed Fung Yip diagnostics and actionable remaining work, without acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-fung-yip-full-native-domain-';BATCH=P+'review-checkpoint-v1-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];phases=[]
 names=[P+s+'-v1-20261024'for s in ['inset','runtime','attributes','replacement-binding','scope','dependency-bindings','native-regression','pairs','support-followthrough','model-scope','native-contacts','foreign-contacts','tower-foundations','tower-complete-clearance','podium-complete-clearance','tower-compound-clearance','podium-effective-heightfield','tower-effective-heightfield','heightfield-grid-conformance','podium-negative-views','tower-compound-negative-views','podium-identity-views','unapproved-browser']]+[P+'exact-boundary-counterexample-v3-20261024']
 results={}
 for n in names:
  r,p=authenticate(BASE/n);results[n]=r;refs.append(BASE/n/'result.json')
  for path,sha in p.items():assert digest((ROOT/path).read_bytes())==sha
  phases.append(dict(batch=n,jobId=r['jobId'],allEvidenceRehashed=True))
 browser=results[P+'unapproved-browser-v1-20261024'];assert browser['privateDiagnosticOnly']and not browser['installationApproved']
 inspection=[]
 for token in ['wall','browser']:
  folder=BASE/(P+token+'-inspection-sheets-v1-20261024');binding=folder/'panel-bindings.json';refs.append(binding)
  for row in read(binding)['rows']:
   path=ROOT/row['path'];assert digest(path.read_bytes())==row['sha256'];refs.append(path)
   for panel in row['panels']:
    key='image'if token=='wall'else'path';sha='imageSHA256'if token=='wall'else'sha256';p=ROOT/panel[key];assert digest(p.read_bytes())==panel[sha];refs.append(p)
   inspection.append(dict(path=row['path'],sha256=row['sha256'],allPanelsActuallyInspected=True,panels=row['panels']))
 critical=BASE/(P+'tower-compound-negative-views-v1-20261024')/'region-5.png';refs.append(critical)
 regression=results[P+'native-regression-v1-20261024'];assert regression['forms']==56 and not regression['basicFlags']and len(regression['nativeRows'])==3 and all(r['passed']for r in regression['nativeRows'])
 result=dict(uids=['landsd/254815:0','landsd/79883:0'],reviewer='ROOT',completedPhases=phases,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,identityAccepted=False,physicalAccepted=False,visualAcceptance=False,privateDesktopMobileAutomatedChecksPassed=True,newlyInstalled=0,currentXLInstalled=355,currentXLUnfinished=166,fixedXLTotal=521,currentDetailedActors=6907,retainedNativeModelsUnchanged=True,all56FormsAnd3RetainedNativeRegressionsPassed=True,imagesActuallyViewed=inspection,criticalFullResolutionImage=dict(path=str(critical.relative_to(ROOT)),sha256=digest(critical.read_bytes())),remainingWork=[
 dict(kind='source-identity-review',uid='landsd/79883:0',reason='Two raw unrelated-footprint flags remain. Exact counterexample proves the proposed4.1mm boundary rule fails at a real4.927408mm interior point. Do not widen the limit, retry identical certificates or mark the source corrupt. Seek independent source-role evidence under authorised unchanged policy.'),
 dict(kind='private-browser-framing',uid='landsd/79882:0',reason='Automated active/frustum/full-bounds checks pass, but ROOT inspected mobile own-source canvases and found foreground tower occlusion. A future qualifying capture must use a clear camera and be inspected; these frames grant no visual acceptance.'),
 dict(kind='physical-source-role-review',uid='landsd/254815:0',reason='All32 unresolved original support probes have finite paths and143 strict contacts in every world. Compound19negative walls have clear-cap paths; faces6520/6525 are under a higher podium roof and must not be described as exposed-top walls. Actual region5 was inspected at full resolution. Full support/identity/physical review remains separate from diagnostic scripts.'),
 dict(kind='qualification-publication',reason='No source review, qualified stage, publisher approval, production installation or live readback exists for this pair. Raw ordinary rim and tiny drawn-projection coverage failures remain. Grid conformance is a conservative sampler envelope, not drawn terrain and not an automatic waiver.')],observations=[
 'Validated exact full old-native extent is210x140m; three retained detailed actors and all56source forms pass unchanged guards. Candidate preserves old target79882 and every government mesh byte/pose. No production terrain edit.',
 'All8actual podium negative wall faces and19tower compound negative faces were inspected via bound scientific panels; the two small tower returns remain explicitly not top-exposed. Source-specific interpretation has not been approved.',
 'Both private devices passed source picking/collision, deliberate download failure/retry and final joint activation. All20source/retained day/night canvas exports were actually inspected. Early mobile own-podium captures contain other companion BASIC fallbacks until their deliberate retry; finaljoint verification is separate.',
 'Retained79882mobile frame is foreground-occluded; desktop podium frames are close and partially occluded. Upton and tower sources are visible; dark original night appearance and other procedural-lit neighbours remain. Passing automated scene checks is not visual approval.',
 'One current grid conformance receipt proves actual geo.js fallback facets/diagonals/heights with9408checks. Raw0.0041807m2drawn holes remain, no renderer/ground change or facet omission. Both sources pass complete actual-ground foundation tests; tower ground clearance is ordinary; podium upper-envelope negatives are all exposed lower walls.' ])
 save(out/'remaining-work.json',result)
 refs.extend(HERE/n for n in ['selected_original_local_inset_v9_20261024.py','selected_original_patch_runtime_v6_20261024.py','selected_retained_native_neighbours_v8_20261024.py','original_effective_heightfield_clearance_v1_20261024.py','verify_virtual_fallback_grid_contract_v1_20261024.mjs','fung_yip_boundary_receipt_readback_v1_20261024.py'])
 module('fung_completed_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-fung-yip-diagnostics-and-actionable-holds',refs,result)
if __name__=='__main__':main()
