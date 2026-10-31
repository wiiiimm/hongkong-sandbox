"""Nominate full retained terrain/domain resources for an existing inset mask.

Metadata-only plan: default mask width is preserved; no installed terrain is cut
off to avoid its obligations. Coordinated nodes remain an explicit blocker.
"""
import argparse
import math
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def overlap(a,b):
    return min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','mask','inventory']:
        p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert not doc.exists()
    mask,mp=authenticate(base/a.mask);_,ip=authenticate(base/a.inventory)
    assert mask['allCompleteOriginalAndLiteralPrimitivesCovered']
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifestpath.read_bytes())
    assert manifest_sha==mp[str(manifestpath.relative_to(ROOT))]==ip[str(manifestpath.relative_to(ROOT))]
    refs=[Path(__file__),base/a.mask/'result.json',base/a.inventory/'result.json',manifestpath]
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath)
    g=root['meta']['georef'];size=root['cell'];assert g['aE']==-g['aN']==size
    x,z,xx,zz=mask['outerBounds']
    cells=[math.floor((x-.001+834500-g['bE'])/size),math.floor((z-.001-816500+g['bN'])/size),
           math.ceil((xx+.001+834500-g['bE'])/size),math.ceil((zz+.001-816500+g['bN'])/size)]
    terrains=[]
    for entry in read(manifestpath)['terrainPatches']:
        path=ROOT/'3d-viewer'/entry['url'];t=read(path)
        if not t.get('nativeMesh') or t['meta'].get('parentTerrain')!='city/data/terrain.json':continue
        terrains.append(dict(url=entry['url'],path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),
            coarseCells=t['coarseCells'],targetUids=t['meta']['targetUids'],
            faces=len(t['nativeMesh']['index'])//3,
            coordinated=bool(t['nativeMesh'].get('source',{}).get('coordinatedBoundary'))))
    retained={};iterations=[]
    while True:
        touched=[t for t in terrains if overlap(cells,t['coarseCells'])]
        expanded=cells[:]
        for row in touched:
            retained[row['url']]=row;s=row['coarseCells']
            expanded=[min(expanded[0],s[0]),min(expanded[1],s[1]),max(expanded[2],s[2]),max(expanded[3],s[3])]
        iterations.append(dict(cells=cells,touchingUrls=[r['url'] for r in touched]))
        if expanded==cells:break
        cells=expanded
        assert len(iterations)<=len(terrains)+1
    bounds=[g['bE']+cells[0]*size-834500,816500-g['bN']+cells[1]*size,
            g['bE']+cells[2]*size-834500,816500-g['bN']+cells[3]*size]
    invpath=base/a.inventory/'complete-bounds.json.gz'
    assert digest(invpath.read_bytes())==ip[str(invpath.relative_to(ROOT))];refs.append(invpath)
    natives=[]
    for row in read(invpath)['rows']:
        allbounds=row['completeFourWorldBounds'];lo=[min(b[0][axis] for b in allbounds) for axis in range(3)];hi=[max(b[1][axis] for b in allbounds) for axis in range(3)]
        if hi[0]>=bounds[0] and lo[0]<=bounds[2] and hi[2]>=bounds[1] and lo[2]<=bounds[3]:natives.append(row['uid'])
    forms=module('retained_domain_forms',HERE/'xl-final-script-pass.py').load_forms(bounds)
    formuids=sorted({b['uid'] for b,_,_ in forms})
    for _,_,tile in forms:
        path=ROOT/'3d-viewer'/tile;assert digest(path.read_bytes())==read(invpath)['currentFormTileHashes'][str(path.relative_to(ROOT))];refs.append(path)
    refs.extend(ROOT/r['path'] for r in retained.values())
    resources=sorted({'building:'+u for u in mask['uids']+natives+formuids}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['url'] for r in retained.values()})
    out=dict(uids=mask['uids'],insetCohort=mask['insetCohort'],coarseCells=cells,bounds=bounds,
        retainedTerrain=list(retained.values()),iterations=iterations,touchingNativeUids=sorted(natives),
        basicFormUids=formuids,resources=resources,coordinatedNodesRequireSeparateContract=any(r['coordinated'] for r in retained.values()),
        sourceGeometryChanges=0,installationApproved=False,
        qualification='Full fixed-point coarse-domain closure over every currently overlapping native root member. Existing return width is unchanged. Full old extents/targets and conservatively intersecting current native/form resources are nominated. No terrain built, replacement/retention proof transferred or coordinated group approved.')
    save(doc/'summary.json',out)
    module('retained_terrain_domain_closure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch,'full-existing-native-terrain-coarse-domain-obligation-closure',list(dict.fromkeys(refs)),out)
    print(dict(cells=cells,retained=len(retained),nativeActors=len(natives),forms=len(formuids),
        retainedFaces=sum(r['faces'] for r in retained.values()),special=out['coordinatedNodesRequireSeparateContract']),flush=True)


if __name__=='__main__':main()
