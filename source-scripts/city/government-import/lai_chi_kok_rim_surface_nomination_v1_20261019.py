"""Complete-face exposed-surface nomination for newly buried platform rim. No edits."""
from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane,lower_region,lift
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lai-chi-kok-rim-surface-nomination-v1-20261019';DOC=BASE/BATCH
def main():
    assert not DOC.exists();prior=BASE/'government-xl-lai-chi-kok-rim-layer-attribution-v1-20261019';r=read(prior/'result.json');refs=[Path(__file__),prior/'result.json',HERE/'source_surface_inset.py']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
    for e in r['evidenceRefs']:
        p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'],p;refs.append(p)
    g=next(x for x in read(HERE/'local/government-xl-lai-chi-kok-eight-runtime-v1-20261019/runtime-geometry.json.gz')['rows']if x['uid']=='landsd/281463:0')
    t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    wanted=read(prior/'summary.json')['incidentSourceFaces'];assert wanted==[19703,19704,19711,19712,19713]
    ps=shapely.polygons(t[:,:,[0,2]]);ids=np.flatnonzero(shapely.area(ps)>1e-10);tree=shapely.STRtree(ps[ids]);planes={int(i):plane(t[i])for i in ids}
    @lru_cache(None)
    def exact(i):
        a,b,c=[[Fraction.from_float(float(x))for x in v]for v in t[i]];u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        return (-n[0]/n[1],-n[2]/n[1],a[1]+(n[0]*a[0]+n[2]*a[2])/n[1])
    out=[];lineage=[];rows=[];vertical=[]
    for i in wanted:
        if i not in planes:vertical.append(i);continue
        cuts=[]
        for j0 in tree.query(ps[i],predicate='intersects'):
            j=int(ids[j0])
            if i==j:continue
            q=ps[i].intersection(ps[j])
            if q.area<=1e-10:continue
            d=planes[j]-planes[i];delta=shapely.get_coordinates(q)@d[:2]+d[2]
            if np.max(np.abs(delta))<=1e-8:
                a,b=exact(i),exact(j)
                if a==b:
                    if j in wanted and j<i:cuts.append(q)
                    continue
                d=np.asarray([float(b[k]-a[k])for k in range(3)])
            higher=lower_region(q,d)
            if higher.area>1e-10:cuts.append(higher)
        exposed=ps[i].difference(shapely.union_all(cuts));fragments=lift(exposed,planes[i]);out.extend(fragments);lineage.extend([i]*len(fragments));rows.append(dict(faceId=i,totalProjectedArea=float(ps[i].area),exposedProjectedArea=float(exposed.area),fragments=len(fragments)))
    out=np.asarray(out).reshape(-1,3,3)
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);gp=shapely.polygons(ground[:,:,[0,2]]);gids=np.flatnonzero(shapely.area(gp)>1e-10);gtree=shapely.STRtree(gp[gids]);conflicts=[]
    for k,f in enumerate(out):
        p=shapely.Polygon(f[:,[0,2]]);fp=plane(f)
        for j0 in gtree.query(p,predicate='intersects'):
            j=int(gids[j0]);q=p.intersection(gp[j])
            if q.area<=1e-10:continue
            d=plane(ground[j])-fp;delta=shapely.get_coordinates(q)@d[:2]+d[2]
            if delta.max()>.5:conflicts.append(dict(sourceFace=lineage[k],fragment=k,terrainFace=j,overlapArea=float(q.area),maxTerrainAboveSource=float(delta.max())))
    summary=dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],faces=rows,verticalFaceIds=vertical,fragments=len(out),exposedTerrainConflictPairs=len(conflicts),installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0)
    save(DOC/'surface-nomination.json.gz',dict(summary=summary,triangles=out.tolist(),sourceFaceIndices=lineage,conflicts=conflicts));save(DOC/'summary.json',summary)
    module('rim_nomination_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-rim-faces-exposed-source-plane-nomination',list(dict.fromkeys(refs)),dict(uids=[g['uid']],summary=summary,installationApproved=False))
    print(summary,flush=True)
if __name__=='__main__':main()
