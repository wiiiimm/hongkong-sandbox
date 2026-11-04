"""Run existing BASIC-neighbour guards across the complete changed parent extent."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import opus_private_terrain_v3_20261016 as prior

BATCH='government-xl-opus-private-neighbours-v2-20261016'
DOC=ROOT/'docs/astra-city/government-import'/BATCH

def main():
    assert not DOC.exists()
    result=read(prior.DOC/'result.json');refs=[Path(__file__),Path(prior.__file__),prior.DOC/'result.json']
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    for ref in result['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'];refs.append(ROOT/ref['path'])
    summary=read(prior.DOC/'summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);pins={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())};native=set()
    for url in m['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;pins[str(p.relative_to(ROOT))]=digest(p.read_bytes());native.update(e['uid']for e in read(p)['models'])
    helper=module('hotel_parent_basic_forms',HERE/'xl-final-script-pass.py');forms=helper.load_forms(summary['changedParentExtent']);rows=[]
    for b,poly,url in forms:
        p=ROOT/'3d-viewer'/url;pins[str(p.relative_to(ROOT))]=digest(p.read_bytes());rows.append(dict(building=b,patchIndexes=[0],existingNative=b['uid']in native))
    candidates=read(prior.DOC/'terrain-candidates.json');assert len(candidates)==1;candidates[0]['uids']=[summary['uid']]
    DOC.mkdir();save(DOC/'neighbour-inputs.json.gz',dict(inputHashes=pins,patches=candidates,candidateIds=[summary['uid']],rows=rows))
    tool=HERE/'check-neighbours.mjs'
    with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
    checked=read(DOC/'neighbour-checks.json');flagged=[r for r in checked['rows']if r['reasons']]
    for p,h in checked['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    refs += [tool,Path(helper.__file__),prior.DOC/'summary.json']
    scope=dict(changedParentExtent=summary['changedParentExtent'],currentForms=len(rows),flagged=flagged,nativeWholePackedVertexScopeStillRequired=True,fullAcceptance=False,newlyInstalled=0)
    save(DOC/'summary.json',scope)
    record=module('hotel_basic_neighbours_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-opus-complete-parent-basic-neighbour-regression-v1',refs,dict(uids=[r['building']['uid']for r in rows],summary=scope,fullAcceptance=False,newlyInstalled=0))
    print(dict(jobId=record['jobId'],summary=scope),flush=True)

if __name__=='__main__':main()
