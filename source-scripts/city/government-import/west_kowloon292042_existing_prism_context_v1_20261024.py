"""Prove the measured neighbouring-boundary overlap remains inside the old BASIC prism."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_convex_projection_coverage_v1_20261024 import rational,intersection,uncovered,area2


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'292042-existing-prism-context-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(s,f):
        n=prefix+s
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take('five-original-runtime-v1-20261024','selection.json.gz');source=next(r for r in selection['rows']if r['uid']=='landsd/255415:0');attr=next(r for r in take('five-original-attributes-v1-20261024','attributes.json.gz')['rows']if r['uid']==source['uid']);basic=take('protected-full-foreign-v1-20261024','basic.json');mesh={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in basic['rows']};old=mesh[source['uid']];foreign=mesh['landsd/292042:0'];ys=np.unique(old[:,:,1]);assert len(ys)==2
    top=old[np.all(old[:,:,1]==ys[1],axis=1)];bottom=old[np.all(old[:,:,1]==ys[0],axis=1)];wall=old[~np.all(old[:,:,1]==ys[0],axis=1)&~np.all(old[:,:,1]==ys[1],axis=1)]
    signature=lambda triangles:Counter(tuple(sorted(map(tuple,t[:,[0,2]])))for t in triangles)
    assert signature(top)==signature(bottom)
    for t in wall:assert area2(rational(t[:,[0,2]]))==0
    edges=Counter(tuple(sorted((tuple(t[a]),tuple(t[b]))))for t in old for a,b in [(0,1),(1,2),(2,0)]if not np.array_equal(t[a],t[b]));assert set(edges.values())=={2}
    cap=[rational(t[:,[0,2]])for t in top];assert all(area2(t)!=0 for t in cap)
    fp=foreign[:,:,[0,2]];rational_foreign=[rational(t)for t in fp];valid=np.asarray([bool(area2(t))for t in rational_foreign]);rational_foreign=[t for t,ok in zip(rational_foreign,valid)if ok];fp=fp[valid];flo,fhi=fp.min(1),fp.max(1)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field]).reshape(-1,3)[ix]
    records=[]
    for mode,tri in worlds.items():
        projection=tri[:,:,[0,2]];lo,hi=projection.min(1),projection.max(1);fragments=[];sourceids=set();candidates=0
        for j,(fl,fh)in enumerate(zip(flo,fhi)):
            for i in np.flatnonzero(np.all(hi>=fl,axis=1)&np.all(lo<=fh,axis=1)):
                candidates+=1;p=rational(projection[i]);poly=intersection(p,rational_foreign[j])
                if not poly or not area2(poly):continue
                assert not uncovered(poly,cap),'Real projection exterior to old BASIC prism'
                assert Fraction.from_float(float(tri[i,:,1].min()))>Fraction.from_float(float(ys[0]))and Fraction.from_float(float(tri[i,:,1].max()))<Fraction.from_float(float(ys[1])),'Original overlap extends beyond old prism height'
                sourceids.add(int(i));fragments.append(dict(sourceFace=int(i),foreignCapFace=j,exactPolygon=[[str(v)for v in q]for q in poly],positiveTwiceArea=str(abs(area2(poly)))))
        assert sourceids=={5223,6292};raw=take('protected-full-foreign-v1-20261024','255415:0--292042:0--'+mode+'.json.gz');assert len(raw['contacts'])==4 and {c['sourceFaceA']for c in raw['contacts']}==sourceids
        save(out/(mode+'.json.gz'),dict(mode=mode,completeSourceWorldSHA256=digest(tri.astype('<f8').tobytes()),completeSourceFaces=len(tri),conservativeProjectionAABBPairs=candidates,positiveAreaFragments=fragments,sourceFaces=sorted(sourceids),rawExactForeignContacts=raw['contacts'],allPositiveProjectionWithinOldPrism=True))
        records.append(dict(mode=mode,sourceFaces=sorted(sourceids),positiveFragments=len(fragments),allPositiveProjectionWithinOldPrism=True,completeSourceWorldSHA256=digest(tri.astype('<f8').tobytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for p,h in basic['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    result=dict(uids=[source['uid'],'landsd/292042:0'],sourceSHA256=source['sourceSHA256'],currentManifestSHA256=selection['manifestSHA256'],oldPrism=dict(completeFaces=len(old),topFaces=len(top),bottomFaces=len(bottom),verticalWallFaces=len(wall),exactYInterval=[str(Fraction.from_float(float(y)))for y in ys],allEdgesHaveTwoIncidentFaces=True,topBottomProjectedTriangulationsIdentical=True),rows=records,sourceGeometryChanges=0,neighbourRetained=True,physicalAccepted=False,installationApproved=False,qualification='Exact rational subtraction checks every positive-area source/actual-foreign projected facet intersection, not sampled points or an area threshold. Each lies in the complete old closed two-level BASIC prism, strictly between its actual floor and roof. All four raw original/foreign contact traces are retained on these same two source facets. This bounds the measured existing boundary intrusion to space already occupied by the before-BASIC model; it does not approve general collision, ownership, arbitrary degenerate-projection containment, source suppression or publication.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_convex_projection_coverage_v1_20261024.py','exact_packed_world_geometry_20261009.py']);module('west_292042_prism_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-four-world-current-boundary-within-before-basic-prism',refs,result);print(records,flush=True)

if __name__=='__main__':main()
