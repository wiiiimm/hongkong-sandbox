"""Prepare an explicit immutable-source dependency proposal; never accept/publish."""
import argparse
import sys
import uuid
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','supports']:p.add_argument('--'+k,required=True)
    p.add_argument('--lease');a=p.parse_args()
    assert all(n.startswith('government-xl-') and '/'not in n for n in [a.batch,a.runtime])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert not out.exists()
    _,pins=authenticate(base/a.runtime);selectionpath=base/a.runtime/'selection.json.gz'
    assert digest(selectionpath.read_bytes())==pins[str(selectionpath.relative_to(ROOT))]
    selected=read(selectionpath);rows=selected['rows'];uids={r['uid']for r in rows}
    assert 0<len(rows)==len(uids)<=40
    supports=(ROOT/a.supports).resolve();assert supports.is_relative_to(base.resolve())
    mapping=read(supports)['supportByUid']
    assert set(mapping)<=uids and set(mapping.values())<=uids
    assert all(uid!=support for uid,support in mapping.items())
    if not a.lease:
        assert not local.exists();lp=local/'reservation.json'
        claim=reservations.claim('original-dependency-proposal-'+str(uuid.uuid4()),sorted('building:'+u for u in uids),batch=a.batch,ttl=3600)
        assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--lease',str(lp)])
    lease=read(Path(a.lease));assert reservations.owns(lease) and {'building:'+u for u in uids}<=set(lease['resources'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']
    sources={r['uid']:r['sourceSHA256']for r in rows};models=[];refs=[Path(__file__),base/a.runtime/'result.json',selectionpath,supports,manifest]
    for r in rows:
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
        entry=deepcopy(r['candidate']['entry']);assert entry['uid']==r['uid'] and entry['sha256']==r['sourceSHA256'] and not entry.get('supportDependencies')
        entry.update(placementReviewed=False,publicationApproved=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        if r['uid']in mapping:entry['supportDependencies']=[dict(uid=mapping[r['uid']],state='candidate',sourceSHA256=sources[mapping[r['uid']]])]
        models.append(entry)
    catalogue=out/'candidate-catalogue.json';save(catalogue,dict(models=models,publication=False,installationApproved=False,qualification='Unapproved exact-source dependency proposal only; assets stay in private cache.'))
    report=from_catalogues(manifest,[catalogue]);save(out/'dependencies.json',report)
    for name,sha in report['inputHashes'].items():
        path=ROOT/name;assert digest(path.read_bytes())==sha;refs.append(path)
    refs.extend([catalogue,out/'dependencies.json',HERE/'dependency_preflight.py'])
    assert reservations.owns(lease) and digest(manifest.read_bytes())==selected['manifestSHA256']
    result=dict(uids=sorted(uids),sourceSHA256ByUid=sources,proposedSupportByUid=mapping,candidateCount=len(rows),requiresAssemblyInvestigation=report['requiresAssemblyInvestigation'],sourceGeometryChanges=0,publication=False,installationApproved=False,qualification=__doc__+' Every approval flag remains false. Publisher dependency-state semantics and current installed catalogue inputs are reused unchanged; no source, physical, terrain, collision or browser approval transfers.')
    save(out/'summary.json',result)
    module('original_dependency_proposal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-original-source-dependency-preflight-proposal',list(dict.fromkeys(refs)),result)
    print(dict(candidates=len(rows),requiresAssemblyInvestigation=report['requiresAssemblyInvestigation']),flush=True)

if __name__=='__main__':main()
