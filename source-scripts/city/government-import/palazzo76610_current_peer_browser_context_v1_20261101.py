"""Bind immutable peer-only facts and inspected browser exports; no installation credit."""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-palazzo76610-after-prosperous-'
BATCH=P+'current-peer-browser-context-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    lp=HERE/'local'/BATCH/'reservation.json';out=BASE/BATCH
    current=read(BASE/(P+'current-fifteen-assembly-context-v1-20261101')/'summary.json')
    resources=sorted('building:'+u for u in current['uids'])
    if not a.owned:
        assert not out.exists()
        c=reservations.claim('palazzo-peer-browser-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==set(resources) and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    current=take(P+'current-fifteen-assembly-context-v1-20261101')
    worlds={r['uid']:r['sourceWorldSHA256ByMode']for r in current['currentGroundContexts']}
    partitions=take('government-xl-palazzo76610-saved-partition-audit-v1-20261031')
    peers=[]
    for r in partitions['rows']:
        mode={'left':'leftF32','balanced':'balancedF32'}.get(r['mode'],r['mode'])
        assert r['sourceWorldSHA256']==worlds[r['uid']][mode]
        assert r['peerWorldSHA256']==worlds['landsd/76610:0'][mode]
        # Old terrain differs: transfer source/peer facts only, never old soil results.
        peers.append({k:r[k]for k in ['uid','mode','sourceWorldSHA256','peerWorldSHA256','negativePeerSourceFaces','nonWallFaces','unresolvedCapFaces']})
    assert len(peers)==44 and all(not r['unresolvedCapFaces']for r in peers)
    shared=take('government-xl-palazzo76610-two-shared-lower-floor-context-v1-20261031')
    assert shared['allLowerPeerCorrespondence']
    lower=[]
    for r in shared['rows']:
        assert r['allFullyFlaggedUpwardFacesHaveLowerPeerCorrespondence']
        assert r['sourceWorldSHA256ByUid']=={u:worlds[u][r['mode']]for u in [r['uid'],'landsd/76610:0']}
        lower.append({k:r[k]for k in ['uid','mode','sourceWorldSHA256ByUid','allFullyFlaggedUpwardFacesHaveLowerPeerCorrespondence']})
    browser=P+'fifteen-private-preview-v2-20261101';br=take(browser)
    assert br['desktopMobileBrowserPassed']and br['atomicCases']==16 and br['sourceSHA256ByUid']==current['sourceSHA256ByUid']
    images=[]
    for width in (1280,390):
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        for uid in current['uids']+['landsd/304700:0']:
            for hour in ('1500','2200'):
                stem=uid.replace('/','-').replace(':','-')
                name=f'staged-retained-own-{stem}-{width}-{hour}.png' if uid=='landsd/304700:0' else f'staged-{stem}-{width}-{hour}-canvas.png'
                path=BASE/browser/str(width)/name
                assert digest(path.read_bytes())==pins[browser][str(path.relative_to(ROOT))]
                refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=uid,width=width,hour=hour))
    assert len(images)==64
    result=dict(uids=current['uids'],sourceSHA256ByUid=current['sourceSHA256ByUid'],currentPeerPartitions=peers,currentSharedLowerFloorCorrespondences=lower,allSavedPeerArraysExactlyCurrent=True,historicalTerrainFactsTransferred=False,desktopMobileBrowserPassed=True,atomicCases=16,images=images,sixtyCandidateExportsInspected=True,nativeOwnExportsInspected=True,reviewer='Codex ROOT',inspectionMethod='Sixty actual candidate exports inspected in four 15-image contact sheets. Some desktop views are tightly cropped; this does not certify complete foundation or adjacent actor visibility. All four native own-view exports were individually inspected; existing native and surrounding BASIC actors remain visible.',sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Exact44 source/peer partitions and shared lower-floor source hashes match the current15 assembly. Current terrain is independently bound by the current assembly receipt. Raw source/peer warnings remain; neither numerical correspondence nor successful browser diagnostics is whole physical/neighbour approval.')
    assert reservations.owns(lease)
    save(out/'summary.json',result)
    module('palazzo_peer_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-peer-and-browser-context-no-approval',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
