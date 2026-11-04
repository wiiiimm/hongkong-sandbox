"""Add the omitted local array pin to a distinct rebound runtime receipt.

All completed thirteen-source loader comparisons and old numeric proofs are
reused unchanged. No capture/attributes/geometry calculations are repeated.
"""
import argparse
import shutil
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-southside-viable-originals-runtime-complete-bindings-v3-20261104'
OLD='government-xl-southside-viable-originals-current-rebind-v2-20261104-runtime'
REPLAY='government-xl-southside-viable-originals-current-rebind-v2-20261104'
OUT=BASE/BATCH
LEASE=HERE/'local'/(BATCH+'-lease')/'reservation.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owned',action='store_true')
    a=p.parse_args()
    assert not OUT.exists()
    replay,_=authenticate(BASE/REPLAY)
    assert replay['oldCompleteLiteralPositionsAndIndicesExactlyEqual'] and replay['freshCompleteActualLoaderPoses']==13
    if not a.owned:
        assert not LEASE.parent.exists()
        claim=reservations.claim('southside-rebound-complete-bindings-'+str(uuid.uuid4()),['building:'+u for u in replay['uids']],batch=BATCH,ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'],LEASE,[sys.executable,__file__,'--owned'])
    lease=read(LEASE)
    assert reservations.owns(lease)
    prior,pins=authenticate(BASE/OLD)
    refs=[Path(__file__),BASE/OLD/'result.json',BASE/REPLAY/'result.json']
    assert prior['uids']==replay['uids']
    for path in (BASE/OLD).iterdir():
        if path.name in ['result.json','neon-sync.json'] or not path.is_file():
            continue
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        target=OUT/path.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
        assert digest(target.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path)
    oldgeometry=HERE/'local'/OLD/'runtime-geometry.json.gz'
    newgeometry=HERE/'local'/BATCH/'runtime-geometry.json.gz'
    original=read(oldgeometry)
    assert sorted(r['uid']for r in original['rows'])==replay['uids']
    # The completed independent replay authenticates every exact full position,
    # index and source SHA; explicitly repeat those comparisons before pinning.
    _,apins=authenticate(BASE/(REPLAY+'-attributes'))
    attributes=BASE/(REPLAY+'-attributes')/'attributes.json.gz'
    assert digest(attributes.read_bytes())==apins[str(attributes.relative_to(ROOT))]
    attrs=read(attributes)
    assert attrs['startEndAllInputsVerified']
    for g in original['rows']:
        attr=next(r for r in attrs['rows']if r['uid']==g['uid'])
        assert attr['sourceSHA256']==g['sourceSHA256']
        assert attr['completeLiteralWorldPosition']==g['position']
        assert attr['completeOriginalIndex']==g['index']
    newgeometry.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(oldgeometry,newgeometry)
    assert digest(newgeometry.read_bytes())==digest(oldgeometry.read_bytes())
    refs += [oldgeometry,newgeometry,attributes,BASE/(REPLAY+'-attributes')/'result.json']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    selected=read(OUT/'selection.json.gz')
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    refs.append(manifest)
    save(OUT/'complete-array-bindings.json',dict(priorRuntimeBatch=OLD,independentReplayBatch=REPLAY,exactCopiedArraySHA256=digest(newgeometry.read_bytes()),completeSourcePosesIndependentlyMatched=13,omittedLocalEvidencePinRepaired=True,calculationsRepeated=False,installationApproved=False))
    result={k:v for k,v in prior.items()if k not in ['jobId','batch','stage','evidenceRefs']}
    result.update(qualification=__doc__,missingLocalPinRepaired=True,independentCompleteSourceReplayJob=replay['jobId'])
    assert reservations.owns(lease)
    module('southside_complete_runtime_bindings_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-rebound-runtime-local-array-bindings',refs,result)


if __name__=='__main__':
    main()
