"""Attribute an unchanged pair foundation envelope failure to actual provider faces.

Observe the existing selector without changing a height, rule or pass/fail result.
"""
import argparse
from collections import Counter
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as exact_gap
from aqua_three_foundation_saved_attribution_v1_20261014 import trace_foundation


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime','attributes','support-proof','supported','support']:
        parser.add_argument('--'+name,required=True)
    a=parser.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert not doc.exists()
    refs,pins=[Path(__file__)],{}
    for name in [a.runtime,a.attributes,a.support_proof]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');selected={r['uid']:r for r in selection['rows']}
    runtime={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    attr=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attr['startEndAllInputsVerified'];attrs={r['uid']:r for r in attr['rows']}
    saved=take(a.support_proof,base/a.support_proof/'summary.json')
    assert saved['supportedUid']==a.supported and saved['supportUid']==a.support
    saved={r['mode']:r for r in saved['rows']}
    modes=['original','literal','leftF32','balancedF32'];worlds={};sources={}
    for uid in [a.supported,a.support]:
        r,at,g=selected[uid],attrs[uid],runtime[uid];asset=ROOT/r['candidate']['path'];raw=asset.read_bytes()
        assert digest(raw)==r['sourceSHA256']==at['sourceSHA256']==g['sourceSHA256'];refs.append(asset);sources[uid]=r['sourceSHA256']
        ix=np.asarray(at['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(raw),**{name:np.asarray(at[key]).reshape(-1,3)[ix] for name,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
    ground=np.asarray(runtime[a.supported]['drawnGroundGeometry']).reshape(-1,3,3)
    form=selected[a.supported]['source']['building'];polygon=Polygon(form['rings'][0],form['rings'][1:])
    final=module('pair_envelope_original_selector',HERE/'xl-final-script-pass.py')
    rows=[]
    for mode in modes:
        target,support=worlds[a.supported][mode],worlds[a.support][mode]
        hashes={u:digest(worlds[u][mode].tobytes()) for u in sources}
        assert hashes==saved[mode]['sourceWorldSHA256ByUid']
        compound=np.concatenate([ground,support])
        foundation,mask,heights=trace_foundation(final,target,compound,polygon,saved[mode]['compoundFoundation'])
        points=np.concatenate([target,target.mean(1)[:,None,:]],axis=1)
        gaps=points[:,:,1]-heights
        bad=np.argwhere(np.isfinite(heights)&(gaps<-.5))
        lo,hi=target.min((0,1)),target.max((0,1))
        keep=(compound[:,:,0].max(1)>=lo[0]-1)&(compound[:,:,0].min(1)<=hi[0]+1)&(compound[:,:,2].max(1)>=lo[2]-1)&(compound[:,:,2].min(1)<=hi[2]+1)
        indices=np.flatnonzero(keep);native=compound[indices]
        polygons=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
        native,polygons,indices=native[valid],polygons[valid],indices[valid]
        tree=shapely.STRtree(polygons)
        badpoints=np.asarray([points[i,j] for i,j in bad])
        pairindex,provider=tree.query(shapely.points(badpoints[:,[0,2]]),predicate='covered_by')
        abc=native[provider];ab=abc[:,1,[0,2]]-abc[:,0,[0,2]];ac=abc[:,2,[0,2]]-abc[:,0,[0,2]];ap=badpoints[pairindex][:,[0,2]]-abc[:,0,[0,2]]
        det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det
        ys=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1])
        chosen={};records=[]
        for k,(sampleindex,nativeindex) in enumerate(zip(pairindex,provider)):
            i,j=map(int,bad[sampleindex])
            if ys[k]!=heights[i,j]:continue
            sourceindex=int(indices[nativeindex]);kind='actual-terrain' if sourceindex<len(ground) else 'support-original'
            faceindex=sourceindex if kind=='actual-terrain' else sourceindex-len(ground)
            face=compound[sourceindex];normal=np.cross(face[1]-face[0],face[2]-face[0]);ratio=float(normal[1]/np.linalg.norm(normal))
            chosen.setdefault(int(sampleindex),[]).append(dict(kind=kind,face=faceindex,normalYRatio=ratio,vertices=face.tolist(),sampledProviderHeightM=float(ys[k])))
        assert set(chosen)==set(range(len(bad)))
        minimum=tuple(map(int,np.unravel_index(np.nanargmin(np.where(np.isfinite(heights),gaps,np.nan)),gaps.shape)))
        for n,(i,j) in enumerate(bad):
            i,j=int(i),int(j);record=dict(sourceFace=i,sampleOrdinal=j,sourcePoint=points[i,j].tolist(),rawGapM=float(gaps[i,j]),highestProviderHeightM=float(heights[i,j]),highestProviders=chosen[n])
            if (i,j)==minimum:
                proofs=[]
                # Recheck this discrete minimum's complete same-XZ column exactly.
                point=points[i,j];xz=compound[:,:,[0,2]]
                allids=np.flatnonzero(np.all(xz.min(1)<=point[[0,2]],axis=1)&np.all(xz.max(1)>=point[[0,2]],axis=1))
                for index in allids:
                    proof=exact_gap(np.repeat(point[None,:],3,axis=0),compound[index])
                    proofs.append(dict(kind='actual-terrain' if index<len(ground) else 'support-original',face=int(index) if index<len(ground) else int(index)-len(ground),proof=proof))
                exact=[Fraction(q['proof']['exactMinimumFiniteColumnGapM']) for q in proofs if q['proof']['exactClosedHorizontalProjectionsMeet']]
                assert exact
                record.update(minimumWitness=True,exactCompleteColumnMinimumGapM=str(min(exact)),exactCompleteColumnProofs=proofs)
            records.append(record)
        save(doc/(mode+'-negative-samples.json.gz'),records)
        categories=Counter(q['kind'] for qs in chosen.values() for q in qs)
        providers=Counter((q['kind'],q['face']) for qs in chosen.values() for q in qs)
        wholeterrainclearance=float(target[:,:,1].min()-ground[:,:,1].max())
        row=dict(mode=mode,sourceWorldSHA256ByUid=hashes,unchangedSavedFoundationReproduced=True,negativeSamples=len(bad),highestProviderKinds=dict(categories),providerFaceCounts=[dict(kind=k,face=i,samples=n) for (k,i),n in sorted(providers.items())],minimumWitness=next(r for r in records if r.get('minimumWitness')),conservativeActualTerrainWholeSourceYGapM=wholeterrainclearance,fullyBuriedTriangles=foundation['fullyBuriedTriangles'],fullyBuriedUpwardTriangles=foundation['fullyBuriedUpwardTriangles'],rawCompoundMinimumGapM=foundation['minimumGapM'],physicalAccepted=False)
        rows.append(row);print({k:row[k] for k in ['mode','negativeSamples','highestProviderKinds','conservativeActualTerrainWholeSourceYGapM','rawCompoundMinimumGapM']},flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    summary=dict(uids=sorted(sources),sourceSHA256ByUid=sources,supportedUid=a.supported,supportUid=a.support,rows=rows,currentManifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Non-mutating observer reproduced each saved fullfoundation aggregate exactly. Everybelow-.5sample attributed to actual highestproviderface(s); discreteglobalminimum independentlychecked against completeexactcolumns. Compoundhighest-source-envelope andactualterrain remain distinct. No providerface removed, contact reclassifiedasaccepted, numericalthreshold changed or support/identity/publicationapproval inferred.')
    save(doc/'summary.json',summary)
    refs.extend(HERE/name for name in ['xl-final-script-pass.py','aqua_three_foundation_saved_attribution_v1_20261014.py','exact_original_triangle_pair_column_gap_20261010.py','exact_packed_world_geometry_20261009.py'])
    module('pair_envelope_attribution_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-pair-compound-envelope-source-attribution',refs,summary)


if __name__=='__main__':
    main()
