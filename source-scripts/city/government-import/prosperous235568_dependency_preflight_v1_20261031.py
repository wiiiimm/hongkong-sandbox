"""Prepare six exact original dependency candidates; no acceptance or publication."""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-prosperous235568'
BATCH=P+'-six-original-dependency-preflight-v1-20261031'
OWNER='landsd/235568:0'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lease',required=True);a=ap.parse_args()
    lease=read(Path(a.lease));assert reservations.owns(lease)
    prior=BASE/(P+'-six-original-patch-runtime-v1-20261031');receipt,pins=authenticate(prior)
    path=prior/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    selection=read(path);rows=selection['rows'];assert len(rows)==6 and len({r['uid']for r in rows})==6
    assert {'building:'+r['uid']for r in rows}<=set(lease['resources'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),prior/'result.json',path,manifest];models=[]
    sources={r['uid']:r['sourceSHA256']for r in rows}
    for r in rows:
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
        entry=deepcopy(r['candidate']['entry']);assert entry['uid']==r['uid'] and entry['sha256']==r['sourceSHA256']
        assert not entry.get('supportDependencies')
        entry.update(placementReviewed=False,publicationApproved=False,identityReviewApproved=False)
        if r['uid']!=OWNER:entry['supportDependencies']=[dict(uid=OWNER,state='candidate',sourceSHA256=sources[OWNER])]
        models.append(entry)
    catalogue=out/'candidate-catalogue.json';save(catalogue,dict(models=models,publication=False,installationApproved=False,qualification='Unapproved exact-source dependency proposal only; assets remain in private acquisition cache.'))
    report=from_catalogues(manifest,[catalogue]);save(out/'dependencies.json',report)
    for name,sha in report['inputHashes'].items():
        p=ROOT/name;assert digest(p.read_bytes())==sha;refs.append(p)
    refs.extend([catalogue,out/'dependencies.json',HERE/'dependency_preflight.py'])
    assert reservations.owns(lease)
    module('prosperous_dependency_preflight_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-original-source-support-dependency-preflight',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,requiresAssemblyInvestigation=report['requiresAssemblyInvestigation'],candidateCount=6,sourceGeometryChanges=0,publication=False,installationApproved=False,qualification='Proposed source dependencies only: five original towers require the exact original podium. All catalogue approval flags remain false. Metadata preflight is independent of whole physical, collision, browser, retained-support and publisher checks.'))

if __name__=='__main__':main()
