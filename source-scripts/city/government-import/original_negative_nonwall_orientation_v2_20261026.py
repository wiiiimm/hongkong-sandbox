"""Record signed orientation of every negative nonwall facet; no approval."""
import argparse,math
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--ground',required=True)
    a=p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.ground])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert not out.exists()
    _,pins=authenticate(base/a.ground)
    refs=[Path(__file__),base/a.ground/'result.json']
    def take(name):
        path=base/a.ground/name
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    summary=take('summary.json');rows=[]
    assert len(summary['rows'])==4 and len({r['mode']for r in summary['rows']})==4
    for mode in summary['rows']:
        detail=take(mode['mode']+'.json.gz')
        assert {r['sourceFace'] for r in detail['rows']} == set(mode['exactAffectedFaces'])
        faces={r['sourceFace'] for r in detail['rows'] if r['absoluteNormalYRatio'] is None or r['absoluteNormalYRatio'] > .25}
        selected=[r for r in detail['rows'] if r['sourceFace'] in faces]
        assert len(selected)==len(faces) and {r['sourceFace']for r in selected}==faces
        facets=[]
        for r in selected:
            a0,b,c=r['vertices'];u=[b[i]-a0[i]for i in range(3)];v=[c[i]-a0[i]for i in range(3)]
            n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            length=math.sqrt(sum(x*x for x in n));assert length>0
            ratio=n[1]/length
            facets.append(dict(sourceFace=r['sourceFace'],signedNormalYRatio=ratio,downward=n[1]<0,upward=n[1]>0))
        rows.append(dict(mode=mode['mode'],sourceWorldSHA256=detail['sourceWorldSHA256'],groundSHA256=detail['groundSHA256'],faces=facets,allDownward=all(f['downward']for f in facets)))
    result=dict(uids=summary['uids'],sourceSHA256=summary['sourceSHA256'],rows=rows,
                installationApproved=False,physicalAcceptance=False,publication=False,newlyInstalled=0,
                sourceGeometryChanges=0,sourcePoseChanges=0,scriptExternalAICalls=0,
                qualification='Signed normals only. Downward orientation is source-role evidence, not an independent acceptance, watertightness or support claim.')
    save(out/'summary.json',result)
    module('negative_nonwall_orientation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-negative-nonwall-complete-orientation-diagnostic',refs,result)
    print([dict(mode=r['mode'],faces=len(r['faces']),allDownward=r['allDownward'])for r in rows],flush=True)


if __name__=='__main__':main()
