"""Admit the exact Yoho original pair to private observation only; preserve all negatives."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 base=ROOT/'docs/astra-city/government-import';batch='government-xl-yoho-mall-ii273672-pair-diagnostic-admission-v1-20261102';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(name,file='summary.json'):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  p=base/name/file;assert digest(p.read_bytes())==pins[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 prefix='government-xl-yoho-mall-ii273672-';runtime=prefix+'two-originals-v2-20261102-runtime'
 selected=take(runtime,'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selected['rows']};assert set(sources)=={'landsd/273672:0','landsd/3007:0'}
 identity=take(prefix+'two-originals-v2-20261102-identity');assert len(identity['rows'])==2 and all(r['passed']and not r['reasons']for r in identity['rows'])
 roots=take(prefix+'original-rooftop-roots-v1-20261102-paths');assert roots['sourceSHA256ByUid']==sources and len(roots['rows'])==4
 assert all(r['targets']==r['finiteAttachmentPaths']==34 and r['disconnected']==r['aboveExistingEndpointCeiling']==0 for r in roots['rows'])
 strict=take(prefix+'two-originals-v2-20261102-support');assert strict['sourceSHA256ByUid']==sources and not strict['allFourModesPassed']
 assert all(r['support']['strictContacts']==6 and len(r['support']['unresolved'])==34 and r['compoundFoundation']['fullyBuriedTriangles']==1 for r in strict['rows'])
 pair=take(prefix+'original-rooftop-pair-context-v1-20261102');assert pair['sourceSHA256ByUid']==sources and len(pair['rows'])==4
 grade=take(prefix+'positive-grade-walls-v1-20261102');assert grade['sourceSHA256']==sources['landsd/273672:0'] and grade['rawCapFailuresPreserved']
 assert all(r['allPositiveFiniteGradeContactsRecomputed']and r['allTopsExceedCompleteLocalGroundUpperBound']and r['minimumExposedMargin']>5 for r in grade['rows'])
 for uid in ['294858','300857']:
  unchanged=take(prefix+'unchanged-native-context-v1-20261102-'+uid);assert unchanged['proposalTerrainNonRegressionProved']and unchanged['existingNativeReaccepted']is False
 scope_name=prefix+'floor-regression-v2-20261102-scope';scope=take(scope_name,'scope.json');forms=take(scope_name,'form-obligations.json.gz');retained=sorted(scope['touchingNativeUids']);assert len(retained)==15
 resources=sorted({('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms}|{'building:'+u for u in retained}|{'terrain:city/data/terrain.json','terrain:city/data/government-native-yoho-mall-i-original-v1-20261020.json'})
 assert {'building:'+u for u in sources}<=set(resources)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifestSHA256=selected['manifestSHA256'],sourceSpecificDiagnosticPreviewAdmitted=True,diagnosticOnly=True,sourceSpecificPhysicalInterpretationAccepted=False,qualifiedForLiveVerification=False,physicalAcceptance=False,installationApproved=False,publication=False,leaseResources=resources,retainedNativeUids=retained,supportByUid={'landsd/3007:0':'landsd/273672:0'},sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictSupportFailures=strict['rows'],rawPairContacts=pair['rows'],rawCapFailuresPreserved=True,qualification='Private observation only. Original rooftop companion recovered exactly, both identities pass and all34 direct rim negatives reach six existing strict roots through unchanged edges below the existing endpoint ceiling. One original wall remains below the maximum podium support envelope; complete contacts retained for source-specific review. Original column walls have actual positive grade intersections and exposed tops, with missing-cap diagnostic preserved. No source role, collision, physical or publication acceptance transferred.')
 save(out/'ROOT-DIAGNOSTIC-ADMISSION.json',result);module('yoho_pair_diagnostic_admission_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-pair-private-observation-admission-only',refs,result)
if __name__=='__main__':main()
