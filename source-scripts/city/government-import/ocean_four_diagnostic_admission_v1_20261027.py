"""Admit exact unapproved original sources to private diagnostics, never publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-after-waterfront-ocean-four-corrected-'
def main():
 base=ROOT/'docs/astra-city/government-import';batch=P+'diagnostic-admission-v1-20261027';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(name,file='summary.json'):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 identity=take(P+'identity-review-v1-20261027');assert identity['identityAccepted']and identity['identityOnlyApproved']and not identity['physicalAcceptance']
 sources=identity['sourceSHA256ByUid'];runtime=take(P+'runtime-v1-20261027','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in runtime['rows']}==sources
 for uid in sources:
  foundation=take(P+uid.split('/')[1].split(':')[0]+'-foundations-v1-20261027')
  assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4 and all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
 native=take(P+'retained-regressions-v1-20261027');assert set(native['nativeResolved'])==set(native['requiredNativeUids'])and all(r['passed']for r in native['nativeRows'])
 assert native['basicFlags']==[dict(uid='landsd/156599:0',reasons=['increased-neighbour-ground-gap'])]
 attachment=take(P+'upper-attachment-revalidation-v1-20261027');assert attachment['sourceOnlyAttachmentEvidenceRevalidated']and not attachment['physicalAcceptance']
 scope=take(P+'regression-scope-v1-20261027','scope.json');forms=take(P+'regression-scope-v1-20261027','form-obligations.json.gz');assert set(scope['touchingNativeUids'])==set(native['requiredNativeUids'])
 patch=take('government-xl-after-waterfront-ocean-four-nested-pair-surface-v1-20261027');assert patch['status']=='private-nested-coordinated-surface-validator-passed'
 assert set(patch['uids'])==set(sources)-{'landsd/156599:0'} and patch['bothEffectiveMembersRequired']
 resources={('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms}|{'building:'+u for u in sources}|{'building:'+u for u in native['requiredNativeUids']}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['url']for r in patch['replacedNativeTerrain']}
 for bound in pins.values():
  for path,sha in bound.items():assert digest((ROOT/path).read_bytes())==sha
 result=dict(uids=list(sources),sourceSHA256ByUid=sources,sourceSpecificDiagnosticPreviewAdmitted=True,diagnosticOnly=True,qualifiedForLiveVerification=False,sourceSpecificPhysicalInterpretationAccepted=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,nativeMetadataChanges=0,supportByUid={'landsd/156599:0':'landsd/234188:0'},retainedNativeUids=native['requiredNativeUids'],leaseResources=sorted(resources),unresolvedSourceInterpretation=['five original podium sloping faces','four original/native interfaces including shared-plane overlap','mixed BASIC/original co-import states'],qualification='Private runtime diagnostics only. Exact approved identities, immutable originals, all four complete source foundations, strict nested terrain retention, all 27 retained native regressions and complete source-only support witness revalidation are prerequisites to display. All grade/interface/root interpretation and original strict warnings remain unresolved. No ROOT-PHYSICAL-REVIEW, source acceptance, private qualification, publisher approval, installed catalogue edit or public terrain write is authorized by this receipt.')
 save(out/'ROOT-DIAGNOSTIC-ADMISSION.json',result);save(out/'summary.json',result);module('ocean_diagnostic_admission_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'unapproved-original-private-diagnostic-admission-only',list(dict.fromkeys(refs)),result)
 print(dict(diagnosticOnly=True,models=len(sources),retained=len(native['requiredNativeUids']),installationApproved=False),flush=True)
if __name__=='__main__':main()
