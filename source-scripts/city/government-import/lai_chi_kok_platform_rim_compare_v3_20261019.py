"""Exact canonical runtime rim/source-terrain comparison; diagnostic only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lai-chi-kok-platform-rim-compare-v3-20261019'
DOC=BASE/BATCH
def main():
    assert not DOC.exists()
    refs=[Path(__file__),HERE/'lai_chi_kok_platform_rim_compare_v3_20261019.mjs'];pins={}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for name in ['government-xl-lai-chi-kok-full-terrain-metrics-v5-20261019','government-xl-lai-chi-kok-all-contact-ground-attribution-v2-20261019']:
            p=BASE/name/'result.json';r=read(p)
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            refs.append(p)
            for e in r['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']]==e['sha256']
                pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    DOC.mkdir(parents=True)
    subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(refs[1]),str(DOC/'comparison.json')],cwd=ROOT,check=True)
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    summary=read(DOC/'comparison.json')['summary']
    module('platform_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'canonical-platform-low-rim-original-terrain-comparison',list(dict.fromkeys(refs)),dict(uids=[summary['uid']],summary=summary,installationApproved=False))
    print(summary,flush=True)
if __name__=='__main__':main()
