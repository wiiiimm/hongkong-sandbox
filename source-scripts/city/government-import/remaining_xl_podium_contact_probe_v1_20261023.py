"""Run canonical original-to-original contact for locally recovered podium nominations."""
from copy import deepcopy
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-remaining-podium-canonical-contacts-v1-20261023';out=base/batch;assert not out.exists()
    prior='government-xl-remaining-floating-podium-discovery-v1-20261023';_,pins=authenticate(base/prior);p=base/prior/'support-candidates.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];nominations=read(p);refs=[Path(__file__),base/prior/'result.json',p];sources={};pairs=[];unavailable=[]
    def add(row):
        uid=row['uid'];old=sources.get(uid)
        if old:assert old['source']==row['source']and old['sourceSHA256']==row['sourceSHA256']and old['candidate']['entry']['sha256']==row['candidate']['entry']['sha256'];return
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
        f=row['source']['building'];row=deepcopy(row);entry=row['candidate']['entry']
        for k,v in [('recordedBaseHeight',f.get('baseHeightHKPD')),('recordedTopHeight',f.get('topHeightHKPD'))]:
            assert k not in entry or entry[k]==v;entry[k]=v
        entry.update(rootTranslation=[-834500,0,816500],proceduralWindows=False)
        sources[uid]=row
    for r in nominations:
        matches=[]
        for asset in r['verifiedLocalOriginalAssets']:
            for m in r['preparedOriginalMatches']:
                model=m['model'];candidate=model.get('candidate')or{}
                if candidate.get('uid')==r['supportUid']and model['asset']['sha256']==asset['sha256']and model['modelId']==asset['modelId']:matches.append((m,asset))
        unique={(m['model']['modelId'],a['sha256']):(m,a)for m,a in matches}
        if len(unique)!=1:
            unavailable.append(dict(uid=r['uid'],supportUid=r['supportUid'],reason='exact-unique-local-support-original-unavailable',matches=len(unique)));continue
        m,a=next(iter(unique.values()));model=m['model'];assert model['candidate']['buildingCSUID']==r['supportForm']['building']['buildingCSUID']
        support=dict(uid=r['supportUid'],modelId=model['modelId'],triangles=model['triangles'],sourceSHA256=a['sha256'],source=r['supportForm'],candidate=dict(path=a['path'],entry=deepcopy(model['candidate'])),native=dict(cacheKey=m['cacheKey'],resultSha=m['resultSHA256'],model=model))
        add(r['source']);add(support);pairs.append(dict(uid=r['uid'],supportUid=r['supportUid']))
    save(out/'support-inputs.json',dict(pairs=pairs,sources=list(sources.values())));save(out/'unavailable.json',unavailable)
    tool=HERE/'original-support-closure-interfaces-incremental.mjs';refs.extend([tool,HERE/'support-interface.mjs',HERE/'source-face-query.mjs'])
    with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(out/'support-checks.json.gz');assert len(report['rows'])==len(pairs)
    for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    rows=[]
    for r in report['rows']:
        i=r['interface'];rows.append(dict(uid=r['uid'],supportUid=r['supportUid'],sourceSHA256=r['sourceSHA256'],supportSHA256=r['supportSHA256'],passed=bool(i and i['passed']),samples=i.get('samples')if i else None,strictContacts=i.get('strictContacts')if i else None,wallIntersections=i.get('wallIntersections')if i else None,unresolved=len(i['unresolved'])if i else None,loadFailure=r.get('loadFailure')))
    result=dict(uids=sorted({u for r in pairs for u in [r['uid'],r['supportUid']]}),pairs=len(pairs),passedPairs=sum(r['passed']for r in rows),unavailablePairs=len(unavailable),rows=rows,sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,status='canonical-original-podium-contact-diagnostics',qualification='Actual production loader with unchanged hash-verified original tower/podium assets and exact current forms. Canonical support interface only: no independent podium terrain, compound identity, all-world contact/clearance, current-neighbour, browser or publication approval.')
    save(out/'summary.json',result);module('remaining_podium_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'canonical-original-podium-support-contact-discovery',refs,result);print(dict(pairs=result['pairs'],passedPairs=result['passedPairs'],unavailablePairs=result['unavailablePairs']),flush=True)

if __name__=='__main__':main()
