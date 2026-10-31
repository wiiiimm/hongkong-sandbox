"""Add completed four-world foundation bindings to the exact 50-form source review."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-inone-five-original-source-review-v3-20261025'
def main():
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    previous='government-xl-inone-five-original-source-review-v2-20261025';physical=take(previous,'ROOT-PHYSICAL-REVIEW.json');source=take(previous,'ROOT-SOURCE-REVIEW.json');assert source==physical
    assert physical['totalNeighbourForms']==50 and physical['terrainAffectedForms']==39
    assert len(physical['leaseResources'])==51 and physical['visualAcceptance']
    selected=take('government-xl-inone-five-required-earth-runtime-v6-20261025','selection.json.gz');rows={r['uid']:r for r in selected['rows']};assert {u:r['sourceSHA256']for u,r in rows.items()}==physical['sourceSHA256ByUid']
    proofs=[]
    for u,row in rows.items():
        batch='government-xl-inone-'+u.split('/')[1].split(':')[0]+'-foundations-v6-20261025';summary=take(batch,'summary.json')
        assert summary['uids']==[u] and len(summary['rows'])==4
        assert {r['mode']for r in summary['rows']}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
        for r in summary['rows']:
            assert r['uid']==u and r['triangles']==r['completeTerrainTriangles']==row['triangles']
            assert r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0
            take(batch,r['mode']+'.json')
        proofs.append(dict(uid=u,batch=batch,completeFaces=row['triangles'],coordinateStreams=4))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()))==physical['currentManifest'];refs.append(manifest)
    result=deepcopy(physical);result.update(completeFourWorldFoundations=True,completeCurrentNeighbourChecks=50,fourWorldFoundationEvidence=proofs,supersedesReview='government-xl-inone-five-original-source-review-v2-20261025')
    result['observations'].append('All five complete-source four-coordinate actual-ground foundation receipts are now bound explicitly. Every stream preserves full source face count with zero wholly buried/wholly buried upward facets. This fills the publisher evidence schema; it changes no source geometry, physical interpretation or guard. The full source/terrain lease union is50forms;39terrain-affected forms have explicit terrain regression checks and the11outside forms have unchanged terrain plus complete model-contact context.')
    out=BASE/BATCH;assert not out.exists();save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('inone_final_foundation_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'inone-five-source-review-complete-foundation-and-neighbour-bindings',refs,result)
if __name__=='__main__':main()
