"""Run the existing Peng TIN constructor for an explicitly checked large source.

Only batch routing changes. All source, terrain, prior-neighbour, runtime and
publication gates remain in the original constructor and subsequent workers.
"""
import argparse
from pathlib import Path
import islands_peng_tin_sweep_stage as engine
from islands_direct_stage import ROOT,HERE,read,save,sha,rel

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);a=p.parse_args();assert a.batch.startswith('government-islands-peng-chau-largest-')and '/'not in a.batch
    engine.BATCH=a.batch;engine.DOC=ROOT/'docs/astra-city/government-import'/a.batch;engine.LOCAL=HERE/'local'/a.batch;engine.STAGE=HERE/'accepted'/a.batch
    engine.main()
    adapter=engine.DOC/'constructor-adapter.json';save(adapter,{'adapter':{'path':rel(Path(__file__)),'sha256':sha(Path(__file__))},'originalKernel':{'path':rel(Path(engine.__file__)),'sha256':sha(Path(engine.__file__))},'changes':['batch routing only'],'sourceGeometryChanges':0,'publication':False})
    for name in ('terrain-stage.json','neighbour-inputs.json.gz'):
        path=engine.DOC/name;data=read(path);data['inputHashes'][rel(adapter)]=sha(adapter);data['inputHashes'][rel(Path(__file__))]=sha(Path(__file__));save(path,data)
