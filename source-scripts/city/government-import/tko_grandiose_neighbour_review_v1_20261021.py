"""Bind current complete neighbour checks and unchanged foreign-contact context."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-neighbour-review-v1-20261021';DOC=BASE/BATCH

def main():
    assert not DOC.exists()
    refs=[Path(__file__)];used={}
    def take(folder,name):
        folder=BASE/folder;receipt,pins=authenticate(folder);p=folder/name
        key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[key]
        used[key]=pins[key];refs.extend([folder/'result.json',p]);return read(p)
    folder='government-xl-tko-grandiose-joint-neighbours-v2-20261021'
    summary=take(folder,'summary.json');native=take(folder,'native-neighbour-checks.json')
    assert summary['ordinaryForms']==230 and len(native['rows'])==12
    checked={r['uid']for r in native['rows']};assert checked==set(summary['requiredNativeUids'])
    assert all(r['passed'] and r['terrain']['newlyWhollyBuried']==0 and r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['rows'])
    assert set(summary['ordinaryFlagged'])=={'landsd/81008:0','landsd/81151:0','landsd/81678:0'}
    assert set(summary['ordinaryFlagged'])<=checked
    for r in native['rows']:
        if r['uid']in summary['ordinaryFlagged']:assert r['support']['supportFraction']>=.5
    assert set(native['stagedOriginalUids'])==set(summary['uids']) and len(summary['uids'])==11
    prior=take('government-xl-grandiose-source-review-v1-20261021','ROOT-SOURCE-REVIEW.json')
    identity=take('government-xl-tko-grandiose-identity-review-v1-20261021','ROOT-IDENTITY-REVIEW.json')
    sources={r['uid']:r['sourceSHA256']for r in identity['rows']}
    assert prior['foreignContactContextAccepted'] and all(sources[u]==sha for u,sha in prior['sourceSHA256ByUid'].items())
    # Old source contact interpretation is reusable because exact assets/poses are unchanged;
    # old terrain acceptance is deliberately replaced by the fresh joint-scene checks.
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
    result=dict(uids=summary['uids'],sourceSHA256ByUid=sources,sourceSpecificNeighbourInterpretationAccepted=True,checkedNativeUids=sorted(checked),ordinaryForms=230,rawOrdinaryFlagsRetained=summary['ordinaryFlagged'],remainingNeighbourFailures=[],conditionalOnInstallingAllSources=native['stagedOriginalUids'],foreignContactContextAccepted=True,foreignContactBasis=prior['foreignContactBasis'],currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),basis='Three coarse flags belong to already installed Grandiose tower originals; their complete-mesh checks pass against the proposed assembly, with no new burial and valid original podium support. All twelve retained originals pass. Other ordinary forms have no flags. Requires all eleven proposed sources and the exact tested joint terrain; not approval for a subset.',installationApproved=False,aiGeometryModelling=False)
    save(DOC/'ROOT-NEIGHBOUR-REVIEW.json',result)
    for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
    module('tko_near_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-joint-neighbour-source-interpretation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
