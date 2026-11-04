"""Candidate-only exact replay of prior residual faces; no whole-model acceptance."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from primrose_compound_foundation_v2_20261015 import module

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','coverage','patch','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    b=ROOT/'docs/astra-city/government-import';out=b/a.batch;assert not out.exists()
    _,rp=authenticate(b/a.runtime);_,cp=authenticate(b/a.coverage);p,pp=authenticate(b/a.patch)
    assert p['status']=='private-terrain-validator-passed'and p['uids']==[a.uid]
    gp=HERE/'local'/a.runtime/'runtime-geometry.json.gz';cpath=b/a.coverage/(a.uid.split('/')[1]+'.json.gz')
    assert digest(gp.read_bytes())==rp[str(gp.relative_to(ROOT))]and digest(cpath.read_bytes())==cp[str(cpath.relative_to(ROOT))]
    g=next(r for r in read(gp)['rows']if r['uid']==a.uid);c=read(cpath);path=ROOT/p['candidate']['path']
    assert digest(path.read_bytes())==p['candidate']['sha256']==pp[str(path.relative_to(ROOT))]
    n=read(path)['nativeMesh'];ground=np.asarray(n['position'],dtype='float32').astype('float64').reshape(-1,3)[np.asarray(n['index']).reshape(-1,3)]
    source=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    assert c['sourceSHA256']==g['sourceSHA256']and digest(source.tobytes())==c['sourceBinding']['decodedWorldTrianglesSHA256']
    proofs=[]
    for old in c['proofs']:
        i=old['sourceFace'];q=exact_coverage(source[i],ground)
        assert q['sourceFaceSHA256']==old['sourceFaceSHA256']
        proofs.append(dict(sourceFace=i,previousExactCoverage=old['exactProjectionCovered'],**q))
        if len(proofs)%25==0:print(dict(checked=len(proofs),total=len(c['proofs'])),flush=True)
    report=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],candidateSHA256=p['candidate']['sha256'],testedPreviousResidualFaces=len(proofs),exactCovered=sum(q['exactProjectionCovered']for q in proofs),stillUncovered=[q['sourceFace']for q in proofs if not q['exactProjectionCovered']],groundFaces=len(ground),proofs=proofs,installationApproved=False,sourceGeometryChanges=0,qualification='Candidate-only diagnostic against stored flat native Float32 coordinates. Tests prior residual source faces only; fresh actual-renderer full-source coverage, foundations, current neighbours, identity and browser remain separate.')
    save(out/'summary.json',report)
    module('candidate_residual_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-original-core-prior-residual-preflight',[Path(__file__),gp,cpath,path,b/a.runtime/'result.json',b/a.coverage/'result.json',b/a.patch/'result.json',HERE/'exact_original_projection_coverage_v2_20261010.py'],report)
    print({k:report[k]for k in ['testedPreviousResidualFaces','exactCovered','stillUncovered']},flush=True)

if __name__=='__main__':main()
