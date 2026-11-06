"""Reuse the unchanged Cheung TIN constructor with unique diagnostic identities."""
import argparse
from pathlib import Path
import islands_cheung_tin_stage as original
from islands_direct_stage import ROOT, HERE, read, save, sha, rel

kernel = original.construct_group
BATCH = None


def construct_group(task):
    number, group, patch, bounds, error = kernel(task)
    if patch is not None:
        patch['id'] = f'{BATCH.removeprefix("government-")}-{number:03d}'
    return number, group, patch, bounds, error


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);a=p.parse_args()
    assert a.batch.startswith('government-islands-cheung-chau-sweep-') and '/' not in a.batch
    global BATCH
    BATCH=a.batch;original.BATCH=BATCH
    original.DOC=ROOT/'docs/astra-city/government-import'/BATCH
    original.LOCAL=HERE/'local'/BATCH;original.STAGE=HERE/'accepted'/BATCH
    original.construct_group=construct_group
    original.main()
    # Only output identity changes. Keep the original kernel code pinned too.
    adapter=original.DOC/'constructor-adapter.json'
    save(adapter,{'adapter':{'path':rel(Path(__file__)),'sha256':sha(Path(__file__))},
        'originalKernel':{'path':rel(Path(original.__file__)),'sha256':sha(Path(original.__file__))},
        'changes':['unique patch id only'],'sourceGeometryChanges':0,'publication':False})
    for name in ('terrain-stage.json','neighbour-inputs.json.gz'):
        path=original.DOC/name;data=read(path)
        data['inputHashes'][rel(adapter)]=sha(adapter)
        data['inputHashes'][rel(Path(__file__))]=sha(Path(__file__))
        save(path,data)


if __name__=='__main__':main()
