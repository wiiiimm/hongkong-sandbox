"""Test the existing native-TIN core argument around exact source bounds.

No model edits, clamp override, new acceptance tolerance or automatic approval.
Original terrain facets fill the bounded core; the existing 10 m parent return
and all current source/neighbour/runtime checks remain mandatory.
"""
import argparse
from pathlib import Path
import numpy as np
import islands_peng_tin_sweep_stage as engine
from islands_direct_stage import ROOT, HERE, read, save, sha, rel

BATCH = None
BOUNDS = {}


def construct_group(task):
    number,group=task;c=engine.CONSTRUCTION;old=c['old'];resolve=old.resolve
    try:
        assert len(group['uids'])==1
        assert not any(old.terrain_helpers.overlap(group['cells'],p['coarseCells'])for p in c['installed_patches'])
        domain=resolve.extent(group['cells'],c['parent']);pieces=[];sources=[]
        for sheet,window in c['windows'].items():
            hit=window.select(domain)
            if not len(hit):continue
            pieces.append(hit);sources.append({**{k:c['proofs'][sheet][k]for k in ('sheet','revisionDate','sourceETag','directorySHA256','compactArchiveSHA256')},'sourceFiles':c['proofs'][sheet]['members']})
        assert pieces
        lo,hi=BOUNDS[group['uids'][0]];core=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]
        patch=resolve.make_patch(group,c['parent'],np.concatenate(pieces),sources,native_core=core,
            parent_sha256=c['parentSHA256'],terrain_triangle_budget=50000)
        patch['id']=f'{BATCH.removeprefix("government-")}-{number:03d}'
        patch['meta']['source']['boundedCore']={'worldBounds':BOUNDS[group['uids'][0]],'marginMetres':2,'core':core,'defaultClampEnforced':True}
        return number,group,patch,domain,None
    except (ValueError,AssertionError)as error:
        return number,group,None,None,str(error)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);a=parser.parse_args()
    assert a.batch.startswith('government-islands-peng-chau-bounded-core-') and '/' not in a.batch
    global BATCH
    BATCH=a.batch;engine.BATCH=BATCH;engine.DOC=ROOT/'docs/astra-city/government-import'/BATCH
    engine.LOCAL=HERE/'local'/BATCH;engine.STAGE=HERE/'accepted'/BATCH
    rows=read(engine.DOC/'nomination.json')['rows'];assert 0<len(rows)<=5
    BOUNDS.update({r['uid']:r['candidate']['entry']['worldBounds']for r in rows})
    assert not {'landsd/190119:0','landsd/297799:0'}.intersection(BOUNDS)
    engine.construct_group=construct_group
    engine.main()
    adapter=engine.DOC/'constructor-adapter.json'
    save(adapter,{'sourceGeometryChanges':0,'defaultClampEnforced':True,'coreMarginMetres':2,
        'source':{'path':rel(Path(__file__)),'sha256':sha(Path(__file__))},
        'baseEngine':{'path':rel(Path(engine.__file__)),'sha256':sha(Path(engine.__file__))},'publication':False})
    for name in ('terrain-stage.json','neighbour-inputs.json.gz'):
        path=engine.DOC/name;data=read(path);data['inputHashes'][rel(adapter)]=sha(adapter)
        data['inputHashes'][rel(Path(__file__))]=sha(Path(__file__));save(path,data)


if __name__=='__main__':main()
