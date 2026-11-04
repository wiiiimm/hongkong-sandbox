"""Extract exact terrain projection gaps for repair without changing any geometry."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,save,digest,read
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract

def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-exact-gap-pieces-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(name,path):
        if name not in cache:cache[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        p=ROOT/path if path.startswith('source-scripts/')else base/name/path
        assert digest(p.read_bytes())==cache[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime='government-xl-island-industrial-paired-current-runtime-v1-20261023';coverage='government-xl-island-industrial-paired-prephysical-20270-v1-20261023-coverage';geometry=take(runtime,'source-scripts/city/government-import/local/'+runtime+'/runtime-geometry.json.gz');rows=[]
    for row in geometry['rows']:
        source=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];ground=np.asarray(row['drawnGroundGeometry']).reshape(-1,3,3);xz=ground[:,:,[0,2]];low=xz.min(1);high=xz.max(1);prior=take(coverage,row['uid'].split('/')[1]+'.json.gz');pieces=[];total=0
        for face in prior['stillUncoveredFaces']:
            t=source[face][:,[0,2]];original=[point(p)for p in t];remaining=[original];ids=np.flatnonzero(np.all(high>=t.min(0),axis=1)&np.all(low<=t.max(0),axis=1))
            if not signed_area(original):pieces.append(dict(sourceFace=face,kind='interval-or-point-needs-separate-finite-proof'));continue
            for i in ids:
                tri=[point(p)for p in xz[i]]
                if signed_area(tri)==0:continue
                remaining=[p for old in remaining for p in subtract(old,tri)]
                if not remaining:break
            area=sum(abs(signed_area(p))for p in remaining);old=next(p for p in prior['proofs']if p['sourceFace']==face)
            assert str(area)==old['exactUncoveredAreaM2']
            values=[dict(rationalXZ=[[str(x),str(z)]for x,z in p],areaM2=str(abs(signed_area(p))),bounds=[float(min(q[0]for q in p)),float(min(q[1]for q in p)),float(max(q[0]for q in p)),float(max(q[1]for q in p))])for p in remaining]
            pieces.append(dict(sourceFace=face,kind='positive-area-gaps',exactUncoveredAreaM2=str(area),pieces=values));total+=float(area)
        save(out/(row['uid'].replace('/','-').replace(':','-')+'.json.gz'),dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],faces=pieces,installationApproved=False))
        rows.append(dict(uid=row['uid'],uncoveredFaces=len(pieces),positiveAreaGapFaces=sum(p['kind']=='positive-area-gaps'for p in pieces),sumFaceGapAreasM2=total,qualification='Sum across source faces may count overlapping projected gaps more than once; not total unique ground gap area.'))
    result=dict(uids=[r['uid']for r in rows],rows=rows,sourceGeometryChanges=0,installationApproved=False,qualification='Exact rational positive-area pieces reproduce every prior failed projection proof. Interval/point gaps remain explicitly separate. Diagnostic for source-backed terrain repair only; no geometry writes, no tolerance credit.')
    save(out/'summary.json',result);refs.append(HERE/'exact_original_projection_coverage_v2_20261010.py');module('gap_pieces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-failed-terrain-projection-gap-extraction',refs,result);print(rows,flush=True)

if __name__=='__main__':main()
