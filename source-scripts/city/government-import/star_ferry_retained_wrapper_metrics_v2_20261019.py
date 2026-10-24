"""Stage the private Star Ferry terrain in the actual regional hierarchy and capture metrics."""
import collections, copy, subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
import native_patch_resolution as repair
import star_ferry_retained_children_candidate_v3_20261019 as runner

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-retained-wrapper-metrics-v2-20261019'
DOC,LOCAL=BASE/BATCH,HERE/'local'/BATCH
SRC=BASE/'government-xl-star-ferry-retained-children-candidate-v3-20261019'

def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    receipt=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json',HERE/'star_ferry_retained_children_candidate_v3_20261019.py']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for e in receipt['evidenceRefs']:
        p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'],str(p);refs.append(p)
    scope=next(r for r in read(runner.SCOPE/'scope.json')['rows'] if r['uid']==runner.UID)
    info=scope['overlappingInstalledTerrain'][0]
    parentpath=ROOT/'3d-viewer'/info['url'];parent=read(parentpath)
    candidatepath=HERE/'local'/SRC.name/'terrain-private-child.json';patch=read(candidatepath)
    plan=read(runner.PROJECTION/'projection-checks.json')
    before=collections.Counter(t.astype('<f4').tobytes() for t in repair._faces(patch))
    checks=[]
    for child in parent['patches']:
        if child['id'] in plan['retainedChildIds']:
            old=collections.Counter(t.astype('<f4').tobytes() for t in repair._faces(child))
            assert not old-before
            checks.append(dict(id=child['id'],retainedTriangles=sum(old.values()),missing=0))
    assert len(checks)==2
    stripped=copy.deepcopy(parent)
    stripped['patches']=[c for c in stripped['patches'] if c['id'] not in plan['retainedChildIds']]
    assert len(stripped['patches'])==len(parent['patches'])-2
    DOC.mkdir(parents=True,exist_ok=True)
    nested=module('star_wrapper',HERE/'xl-stage-central-nested.py');nested.DOC=DOC
    wrapper=nested.parent_with_nested(stripped,patch)
    assert wrapper['elev']==parent['elev'] and wrapper.get('renderedElev')==parent.get('renderedElev')
    for a,b in zip(stripped['patches'],wrapper['patches']):
        for key in ['elev','renderedElev']:assert a.get(key)==b.get(key)
        for key in ['position','index']:assert a.get('nativeMesh',{}).get(key)==b.get('nativeMesh',{}).get(key)
    builder=module('star_wrapper_validator',HERE/'resolve-pass-indexed-parent-clipping.py')
    builder.validate_patch(wrapper,read(ROOT/'3d-viewer/city/data/terrain.json'))
    out=LOCAL/'terrain-star-ferry.json';save(out,wrapper)
    save(DOC/'retained-proof.json',dict(children=checks,otherChildrenUnchanged=len(stripped['patches']),installationApproved=False))
    save(DOC/'terrain-candidates.json',[dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=[runner.UID],coarseCells=plan['mergedCells'],replaces=dict(url=info['url'],sha256=digest(parentpath.read_bytes()),retainedUids=info['parentNativeUids']))])
    selection=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz'
    row=next(r for r in read(selection)['rows'] if r['uid']==runner.UID)
    asset=LOCAL/row['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True)
    raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset.write_bytes(raw)
    row['candidate']['path']=str(asset.relative_to(ROOT))
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(manifest.read_bytes())))
    command=['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
    with (DOC/'worker.log').open('w') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    metrics=read(DOC/'metrics.json')
    for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    refs.extend([candidatepath,parentpath,manifest,selection,HERE/'xl-stage-central-nested.py',HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py'])
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json')
    assert reservations.owns(lease)
    module('star_wrapper_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-staged-retained-regional-terrain-metrics',list(dict.fromkeys(refs)),dict(uids=[runner.UID],metrics=metrics['rows'],installationApproved=False))
    print(metrics['rows'],flush=True)

if __name__=='__main__':
    runner.BATCH,runner.DOC,runner.LOCAL=BATCH,DOC,LOCAL
    runner.owned=owned
    # The lease runner invokes its own __file__; point it at this continuation.
    runner.__file__=str(Path(__file__).resolve())
    runner.main()
