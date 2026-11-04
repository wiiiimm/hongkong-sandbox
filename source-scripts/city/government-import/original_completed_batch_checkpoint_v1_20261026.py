"""Archive completed current-source receipts; never infer installation or approval."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','prefix','installed','selection','expected-receipts']:
        p.add_argument('--'+k,required=True,type=int if k=='expected-receipts' else str)
    p.add_argument('--prior-progress',action='append',default=[])
    p.add_argument('--viewed-export',action='append',default=[])
    p.add_argument('--next-action',action='append',required=True)
    a=p.parse_args()
    assert all(s.startswith('government-xl-')and'/'not in s for s in [a.batch,a.prefix,a.installed,a.selection,*a.prior_progress])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs,checked,completed=[Path(__file__)],{},[]
    for folder in sorted(base.glob(a.prefix+'*')):
        if folder==out or not(folder/'result.json').exists():continue
        receipt,pins=authenticate(folder)
        for path,sha in pins.items():
            assert path not in checked or checked[path]==sha
            if path not in checked:
                assert digest((ROOT/path).read_bytes())==sha,path
                checked[path]=sha
        refs.append(folder/'result.json');completed.append(dict(batch=folder.name,jobId=receipt['jobId'],verifiedFiles=len(pins)))
    assert len(completed)==a.expected_receipts,(len(completed),a.expected_receipts)
    installed,pins=authenticate(base/a.installed);count=base/a.installed/'full-xl-current-count.json'
    assert digest(count.read_bytes())==pins[str(count.relative_to(ROOT))]
    report=read(count);assert len(report['rows'])==521
    selected,selectionpins=authenticate(base/a.selection);selection=base/a.selection/'selection.json.gz'
    assert digest(selection.read_bytes())==selectionpins[str(selection.relative_to(ROOT))]
    sources={r['uid']:r['sourceSHA256']for r in read(selection)['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==report['manifestSHA256']==selected['currentManifestSHA256']
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert read(pointer)['snapshotId']==installed['snapshotId']
    refs.extend([count,base/a.installed/'result.json',selection,base/a.selection/'result.json',manifest,pointer])
    historical=[]
    for name in a.prior_progress:
        receipt,_=authenticate(base/name);path=base/name/'result.json';refs.append(path)
        historical.append(dict(batch=name,jobId=receipt['jobId'],receiptSHA256=digest(path.read_bytes()),currentSceneAcceptanceTransferred=False))
    images=[]
    for name in a.viewed_export:
        path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)and digest(path.read_bytes())==checked[str(path.relative_to(ROOT))]
        refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,completedJobs=completed,verifiedEvidenceFiles=len(checked),
                fullXLCurrentCounts=report['counts'],completeFixedXLRows=521,nullViewerUIDSourceKeysRetained=sum(r.get('uid')is None for r in report['rows']),
                officialDetailedActors=installed['completeCurrentCatalogueModels'],historicalProgress=historical,imagesActuallyOpenedByRoot=images,
                nextActions=a.next_action,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,
                physicalAcceptance=False,identityAccepted=False,publication=False,newlyInstalled=0,allXLGoalComplete=False,
                aiGeometryModelling=False,scriptExternalAICalls=0,
                qualification='Completed current original-source computation and authenticated evidence archive only. Prior snapshots remain historical. Every selected source still needs its applicable exact identity, physical-role, dependency, browser and guarded publication decisions. No optimisation or production queues written.')
    save(out/'remaining-work.json',result)
    module('original_completed_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch,'completed-current-original-source-batch-and-full-xl-continuation',list(dict.fromkeys(refs)),result)
    print(dict(completedJobs=len(completed),verifiedFiles=len(checked),counts=report['counts']),flush=True)


if __name__=='__main__':main()
