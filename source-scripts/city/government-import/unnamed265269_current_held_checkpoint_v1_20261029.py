"""Bind the completed current unnamed-source checks to actionable retained holds."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed265269-current-held-checkpoint-v1-20261029';P='government-xl-unnamed265269-current-evidence-v1-20261029'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];inputs={};data={}
    records=dict(identity=(P+'-identity','265269:0/identity.json'),foundations=(P+'-foundation-265269-0','summary.json'),scope=(P+'-model-scope','summary.json'),foreign=('government-xl-unnamed265269-current-foreign-contacts-v1-20261029','summary.json'),lookup=('government-xl-unnamed265269-raw-canopy-georef-lookup-v2-20261029','lookup.json'),views=('government-xl-unnamed265269-current-identity-views-v1-20261029','summary.json'),interface=('government-xl-unnamed265269-canopy-interface-views-v1-20261029','summary.json'))
    for k,(batch,name)in records.items():
        receipt,pins=authenticate(BASE/batch);p=BASE/batch/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
        refs.extend([BASE/batch/'result.json',p]);data[k]=read(p);inputs[k]=dict(jobId=receipt['jobId'],path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    assert data['foundations']['establishedFoundationPolicyPassed']and not data['identity']['passed']
    assert not data['scope']['rows'][0]['nearbyNativeActors']
    pairs=data['foreign']['rows'];assert len(pairs)==5
    positive=[r for r in pairs if any(m['positiveContactPairs']for m in r['modes'])];assert len(positive)==1 and positive[0]['foreignUid']=='landsd/265270:0'
    assert all(m['positiveContactPairs']==(24 if m['mode']=='before-basic'else 28)for m in positive[0]['modes'])
    assert len(data['lookup']['rows'])==1 and data['lookup']['rows'][0]['matchCount']==0
    images=[BASE/records['views'][0]/n for n in ['whole-source-plan.png','whole-source-perspectives.png']]+[BASE/records['interface'][0]/n for n in ['full-height.png','original-height.png']];refs.extend(images)
    result=dict(uids=['landsd/265269:0'],sourceSHA256='0adf753f5832d3598fd1d99c3700b704e33de74aa97c4d4f868ba68c6cb445da',humanStatus='held for continued scripted source/interface recovery',humanDecisionRequired=False,aiGeometryRequired=False,permanentRejection=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,inputs=inputs,completeFourWorldFoundationPolicyPassed=True,currentNativeActorsChecked=7016,nearbyInstalledNativeActors=[],foreignPairs=5,foreignPairsClearBeforeAndAfter=4,canopyPositiveContactsBefore=24,canopyPositiveContactsAfterPerWorld=28,imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],heldReasons=[dict(reason='Full original source extent and canopy relationship need review',rawIdentityReasons=data['identity']['reasons'],observed='Whole source is a long connected roof/building with authored extensions. Exterior projected overlap alone is not source identity approval; the separate263686form has no positive finite contact in before and all4source worlds.'),dict(reason='Retained open-sided canopy265270 interface unresolved',observed='Actual captured original contains a higher canopy/columns at this footprint; BASIC roof and posts remain lower and contacts increase24to28. No suppression or BASIC height edit approved. Exact viewer-match and rawGeoRef owner-cache lookup both return no separate canopy model; this is not provider-wide absence.')],nextActions=['Search other pinned cached source records for the exact canopy GeoRef; raw provider directory lookup only under existing acquisition/storage guard.','Test exact complete source-roof and post-footprint coverage using existing canopy/fallback policies.','Preserve every raw identity/contact/ground warning; approve no suppression without a source-bound complete counterpart proof.','Resolve ordinary rim/cap roles and run actual private desktop/mobile/fallback/collision checks before installation.'])
    save(out/'held-reasons.json',result)
    module('unnamed_held_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-unnamed-original-actionable-source-interface-held-checkpoint',refs,result)
if __name__=='__main__':main()
