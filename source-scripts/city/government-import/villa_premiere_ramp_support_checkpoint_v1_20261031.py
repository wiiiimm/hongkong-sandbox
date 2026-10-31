"""Bind unchanged strict-root witnesses to fresh Villa Premiere ramp-ground checks."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-villa-premiere89917-'
BATCH=P+'ramp-support-checkpoint-v1-20261031'

def main():
    out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(batch,name='summary.json'):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rows=[]
    for key in ['58497','63823','121309','148052']:
        uid='landsd/'+key+':0';old=take(P+key+'-0-podium-support-v1-20261030');fresh=take(P+key+'-0-ramp-compound-v1-20261030');paths_batch=P+key+'-0-strict-root-paths-v1-20261030';paths=take(paths_batch)
        assert old['supportedUid']==fresh['supportedUid']==uid and old['supportUid']==fresh['supportUid']=='landsd/89917:0'
        assert old['sourceSHA256ByUid']==fresh['sourceSHA256ByUid']==paths['sourceSHA256ByUid']
        assert len(old['rows'])==len(fresh['rows'])==len(paths['rows'])==4
        modes=[]
        for mode in ['original','literal','leftF32','balancedF32']:
            before=next(r for r in old['rows']if r['mode']==mode);after=next(r for r in fresh['rows']if r['mode']==mode)
            assert before['sourceWorldSHA256ByUid']==after['sourceWorldSHA256ByUid'] and before['support']==after['support']
            proof=take(paths_batch,mode+'.json.gz');summary=next(r for r in paths['rows']if r['mode']==mode)
            assert proof['sourceWorldSHA256']==after['sourceWorldSHA256ByUid'][uid]
            assert proof['supportWorldSHA256']==after['sourceWorldSHA256ByUid']['landsd/89917:0']
            assert proof['noIntercomponentJoins']and proof['originalEndpointHeightGatePreserved']
            assert summary['targets']==summary['finiteAttachmentPaths'] and summary['disconnected']==summary['aboveExistingEndpointCeiling']==0
            assert [r['witness']for r in proof['rows']]==after['support']['unresolved']
            assert all(r['hasUnrestrictedFiniteAttachment']and r['riseAboveEndpointsM']<=0 for r in proof['rows'])
            foundation=after['compoundFoundation'];assert foundation['fullyBuriedTriangles']==foundation['fullyBuriedUpwardTriangles']==0
            modes.append(dict(mode=mode,exactSourceAndSupportArraysUnchanged=True,exactDirectWarningSetUnchanged=True,finitePaths=summary['finiteAttachmentPaths'],freshCompoundBuriedFaces=0))
        rows.append(dict(uid=uid,modes=modes,rawDirectInterfacePassed=fresh['allFourModesPassed']))
    cap=take(P+'five-ramp-podium-caps-v1-20261030');assert cap['allFourCompleteGroundClearCapPaths']
    foreign=take(P+'five-ramp-foreign-contacts-v1-20261030');uids=set(foreign['uids']);assert len(uids)==5
    unrelated=[r for r in foreign['rows']if r['foreignUid']not in uids]
    assert all(m['positiveContactPairs']==0 for r in unrelated for m in r['modes']if m['mode']!='before-basic')
    canopy=take(P+'canopy-post-foundation-v1-20261030');assert canopy['fullPostFootprintsMeetGround']and canopy['wholeRoofClear']and canopy['completePostCount']==8
    result=dict(uids=sorted(uids),rows=rows,exactStrictRootWitnessesReusable=True,allFourPodiumCapProofsPass=True,foreignPairs=foreign['foreignPairs'],unrelatedBasicPairs=len(unrelated),unrelatedPositiveSourceContacts=0,privateCanopyPosts=8,privateCanopyFoundationBase=canopy['foundationBase'],sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,identityAccepted=False,physicalAcceptance=False,browserAcceptancePending=True,qualification='Exact current source/support array hashes and complete raw warning tuples match the existing canonical strict-root proofs. Every remaining tower witness has a finite shared-original-edge path without endpoint rise; fresh compound foundations have zero buried faces. All four podium cap proofs pass. Complete scoped foreign BASIC contacts contain no positive source contacts outside the five co-import fallback forms. The existing unsurveyed canopy post-bottom-only proposal passes full footprint and roof checks. This reuses unchanged witnesses, preserves raw direct-interface failures and grants no identity, source-role, full neighbour, collision, browser or publication acceptance.')
    save(out/'summary.json',result)
    module('villa_ramp_support_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-ramp-support-evidence-checkpoint',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
