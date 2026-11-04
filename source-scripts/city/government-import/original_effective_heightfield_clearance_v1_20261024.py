"""Conservative clearance against drawn native facets AND its existing grid fallback.

The grid is an overestimate: the runtime uses it only when native.height is null.
Diagnostic virtual facets are never published or described as drawn geometry.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--patch',required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[Path(__file__)]
    for name in [a.runtime,a.attributes]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz')['rows']
    row=next(r for r in selection if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attributes=take(a.attributes,base/a.attributes/'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attr=next(r for r in attributes['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(raw),**{name:np.asarray(attr[key]).reshape(-1,3)[ix]for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    actualground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(actualground)>0
    patch_receipt,patch_pins=authenticate(base/a.patch);refs.append(base/a.patch/'result.json')
    path=ROOT/patch_receipt['candidate']['path'];assert digest(path.read_bytes())==patch_receipt['candidate']['sha256']==patch_pins[str(path.relative_to(ROOT))];refs.append(path);patch=read(path)
    marker=patch['nativeMesh']['source']['numericalCoverageGap'];assert marker['policy']=='parent-grid-fallback'and marker['maximumAreaM2']<=.25 and marker['measuredAreaM2']<=marker['maximumAreaM2']
    assert digest(path.read_bytes())==pins[a.runtime][str(path.relative_to(ROOT))]
    gref=patch['meta']['georef'];w,h=patch['w'],patch['h'];vertices=[]
    for rr in range(h):
        for cc in range(w):
            k=rr*w+cc;y=patch.get('renderedElev',[])[k]if patch.get('renderedElev')else None
            if y is None:y=max(1.2,patch['elev'][k])if patch['elev'][k]>0 else -4
            vertices.append([gref['bE']+cc*gref['aE']-834500,y,816500-gref['bN']-rr*gref['aN']])
    vertices=np.asarray(vertices,float);assert np.isfinite(vertices).all();grid=[]
    for rr in range(h-1):
        for cc in range(w-1):
            i=rr*w+cc;grid.extend([vertices[[i,i+1,i+w]],vertices[[i+w+1,i+w,i+1]]])
    grid=np.asarray(grid);complete=np.concatenate([t.reshape(-1,3)for t in modes.values()]);lo,hi=complete.min(0),complete.max(0)
    assert vertices[:,0].min()<lo[0]<=hi[0]<vertices[:,0].max()and vertices[:,2].min()<lo[2]<=hi[2]<vertices[:,2].max(),'All original source projections must lie strictly inside the fallback domain'
    grid=grid[np.all(grid[:,:,[0,2]].max(1)>=lo[[0,2]],axis=1)&np.all(grid[:,:,[0,2]].min(1)<=hi[[0,2]],axis=1)]
    assert len(grid)>0;effective_ground=np.concatenate([actualground,grid]);save(out/'heightfield-contract.json',dict(actualDrawnGroundSHA256=digest(actualground.tobytes()),virtualFallbackTriangles=len(grid),virtualFallbackSHA256=digest(grid.tobytes()),effectiveUpperEnvelopeSHA256=digest(effective_ground.tobytes()),completeSourceFourWorldBounds=[lo.tolist(),hi.tolist()],numericGapDeclaration=marker,sourceGeometryChanges=0,terrainGeometryChanges=0,publication=False,qualification='Current geo.js selects the finite native surface, or its grid on a declared numeric gap. The union used here includes that grid everywhere under the source bounds, so it conservatively overestimates the actual sampler. It is diagnostic only; no virtual facet is drawn or published. Raw missing drawn-projection diagnostics remain unchanged.'))
    refs.extend([ROOT/'3d-viewer/city/geo.js',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/exact-finite-triangle-projection.js',ROOT/'3d-viewer/city/world.js'])
    threshold=Fraction(-1,2);summaries=[]
    from complete_clearance_cap_paths_v2_20261024 import verify as cap_verify
    from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
    for name,tri in modes.items():
        assert len(tri)==row['triangles'];rows=[];pruned=0;checked=0
        ground=effective_ground
        gxz=ground[:,:,[0,2]];glo=gxz.min(1);ghi=gxz.max(1);maxy=Fraction(float(ground[:,:,1].max()))
        for i,t in enumerate(tri):
            if Fraction(float(t[:,1].min()))-maxy>=threshold:pruned+=1;continue
            txz=t[:,[0,2]];ids=np.flatnonzero(np.all(ghi>=txz.min(0),axis=1)&np.all(glo<=txz.max(0),axis=1));proofs=[]
            for j in ids:
                proof=verify(t,ground[j]);checked+=1
                if proof['exactClosedHorizontalProjectionsMeet']and Fraction(proof['exactMinimumFiniteColumnGapM'])<threshold:proofs.append(dict(groundFace=int(j),proof=proof))
            if not proofs:continue
            cross=np.cross(t[1]-t[0],t[2]-t[0]);norm=float(np.linalg.norm(cross));ratio=abs(float(cross[1]))/norm if norm else None
            v=int(np.argmax(t[:,1]));point=t[v];pis=np.flatnonzero(np.all(glo<=point[[0,2]],axis=1)&np.all(ghi>=point[[0,2]],axis=1));exposed=[]
            for j in pis:
                proof=verify(np.repeat(point[None,:],3,axis=0),ground[j])
                if proof['exactClosedHorizontalProjectionsMeet']:exposed.append(dict(groundFace=int(j),proof=proof))
            rows.append(dict(sourceFace=i,vertices=t.tolist(),absoluteNormalYRatio=ratio,minimumFiniteGapM=str(min(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])for q in proofs)),negativeGroundPairProofs=proofs,highestOriginalVertex=v,highestVertexProofs=exposed,highestVertexAboveEveryOverlappingGroundFace=bool(exposed)and all(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])>0 for q in exposed)))
        save(out/(name+'.json.gz'),dict(sourceWorldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),rows=rows,completeSourceFaces=len(tri),globalHeightBoundPrunedFaces=pruned,finitePairsTested=checked))
        affected=[r['sourceFace'] for r in rows]
        initial=cap_verify(tri,affected)
        unresolved=[p['sourceFace'] for p in initial['paths'] if not p['hasExactSharedEdgeClearCapPath']]
        contacts=[]
        if unresolved:
            partial=exact_finite_contacts(tri,unresolved,tri,list(range(len(tri))))
            save(out/(name+'-partial-contacts.json.gz'),partial)
            contacts=sorted({tuple(sorted((c['sourceFaceA'],c['sourceFaceB']))) for c in partial['contacts'] if c['sourceFaceA']!=c['sourceFaceB'] and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2})
        cap=cap_verify(tri,affected,contacts)
        save(out/(name+'-cap-paths.json.gz'),dict(compoundGroundSHA256=digest(ground.tobytes()),sourceWorldSHA256=digest(tri.tobytes()),actualGroundSHA256=digest(actualground.tobytes()),proof=cap))
        summaries.append(dict(compoundCapPathsPassed=cap['allAffectedHavePaths'],noAffectedFaces=not affected,negativeNonWallFaces=cap['negativeNonWallFaces'],mode=name,completeSourceFaces=len(tri),globalHeightBoundPrunedFaces=pruned,finitePairsTested=checked,exactAffectedFaces=[r['sourceFace']for r in rows],allAffectedWallLike=all(r['absoluteNormalYRatio']is not None and r['absoluteNormalYRatio']<.25 for r in rows),allAffectedHaveExposedHighestVertex=all(r['highestVertexAboveEveryOverlappingGroundFace']for r in rows)))
        print(summaries[-1],flush=True)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],rows=summaries,installationApproved=False,physicalAcceptance=False,architectureReview=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Every source face considered against ALL actual drawn facets PLUS the full current grid-fallback envelope under the source in each coordinate stream. The grid is a conservative sampler overestimate, never claimed drawn ground; raw drawn-projection gaps remain.  Exact source-positive-contact clear-cap paths verified using that complete negative partition. Empty negative sets need no cap path. No model support geometry or support height is used. No source-role, support, identity, dependency replacement or publication approval.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_triangle_pair_column_gap_20261010.py','complete_clearance_cap_paths_v2_20261024.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
    module('actual_ground_complete_clearance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-complete-source-low-face-exact-current-ground-context',refs,result)


if __name__=='__main__':main()
