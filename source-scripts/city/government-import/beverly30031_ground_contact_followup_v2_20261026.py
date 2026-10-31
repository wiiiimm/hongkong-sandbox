"""Persist the exact unresolved original-ground contact; never grant acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    prefix='government-xl-after-qe-beverly30031-'
    batch=prefix+'ground-contact-followup-v2-20261026'
    out=base/batch
    assert not out.exists()
    refs=[Path(__file__)]
    def take(suffix,filename):
        folder=base/(prefix+suffix+'-20261026')
        receipt,pins=authenticate(folder)
        path=folder/filename
        if filename=='result.json':
            refs.append(path)
            return receipt,receipt
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.extend([folder/'result.json',path])
        return read(path),receipt
    metrics,_=take('retained-runtime-v1','metrics.json')
    selection,_=take('retained-runtime-v1','selection.json.gz')
    identity,_=take('identity-v1','summary.json')
    foundation,_=take('retained-foundations-v1','summary.json')
    negatives,_=take('retained-low-faces-v1','summary.json')
    decisions,_=take('native-terrain-decisions-v2','summary.json')
    browser,_=take('private-browser-v1','result.json')
    uid='landsd/30031:0'
    row=next(r for r in selection['rows']if r['uid']==uid)
    metric=next(r for r in metrics['rows']if r['uid']==uid)
    assert row['sourceSHA256']==metric['sourceSHA256']=='19a98fa6709619ab7ec32664025d15c084f458b4890f4b5db85d1fd36035b587'
    assert identity['rows']==[dict(passed=True,reasons=[],sourceSHA256=row['sourceSHA256'],uid=uid)]
    # Reproduce the existing policy, including its failed contact gate.
    policy=module('beverly_original_policy',HERE/'acceptance-policy.py')
    refs.append(HERE/'acceptance-policy.py')
    policyrow=dict(row,state='runtime-validated-awaiting-acceptance')
    reasons=policy.reasons(policyrow,metric,metrics['profiles']['mobile'])
    assert reasons==['ground-contact-unresolved']
    assert metric['lowRimChecks']==480 and metric['missingTerrain']==0
    assert .1<metric['minLowGap']<=metric['maxLowGap']<1
    assert len(foundation['rows'])==4 and all(r['establishedFoundationPolicyPassed']and r['fullyBuriedTriangles']==0 and r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    assert len(negatives['rows'])==4 and all(not r['exactAffectedFaces']for r in negatives['rows'])
    assert browser['allBrowserDiagnosticsPassed']and browser['rawRetainedNativeFailures']==decisions['rawNativeFailures']
    assert len(decisions['requiredNativeUids'])==22 and len(decisions['rawNativeResolved'])==19 and len(decisions['rawNativeFailures'])==3
    assert decisions['allTerrainChangeDecisionsPassed']and not decisions['existingNativeReaccepted']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256']==decisions['currentManifestSHA256']
    refs.append(manifest)
    result=dict(uids=[uid],sourceSHA256=row['sourceSHA256'],completeSourceFaces=10434,
        currentManifestSHA256=selection['manifestSHA256'],rawAcceptanceReasons=reasons,
        lowRimChecks=metric['lowRimChecks'],minimumLowGapM=metric['minLowGap'],maximumLowGapM=metric['maxLowGap'],
        wholeFourWorldFoundations=foundation['rows'],rawRetainedNativeFailures=decisions['rawNativeFailures'],
        strictNativePasses=19,terrainNonRegressionDecisions=22,existingNativeReaccepted=False,
        privateBrowserDiagnosticsPassed=True,completeVisualReview=False,
        humanStatus='In process',executionState='queued-source-ground-contact-investigation',
        nextAction='Check authentic source/terrain revision and any genuine lower source support for the 480 raised rim samples. Preserve fixed placement and raw contact failure. Do not invent terrain, translate the model or waive the 0.1m minimum-contact gate.',
        humanDecisionRequired=False,aiGeometryModellingRequired=False,permanentRejection=False,
        installationApproved=False,physicalAcceptance=False,publication=False,newlyInstalled=0,
        sourceGeometryChanges=0,sourcePoseChanges=0,scriptExternalAICalls=0,
        qualification='All burial checks and terrain-change non-regression are distinct from the unresolved direct ground contact. The original mesh remains uninstalled. Browser diagnostics are not visual acceptance; ROOT observed foreground occlusion in the first source export, and a separate opposite-angle run is in progress. No engineering-root, support, source-corruption or permanent-rejection inference.')
    save(out/'summary.json',result)
    module('beverly_ground_followup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-ground-contact-pending-followup',list(dict.fromkeys(refs)),result)
    print(dict(batch=batch,rawAcceptanceReasons=reasons,newlyInstalled=0),flush=True)

if __name__=='__main__':main()
