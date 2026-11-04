"""Exact source lower-face context against complete current terrain and one peer.

Diagnostic only. The unchanged strict compound-foundation failure remains saved.
Both source and peer world hashes bind each independently measured stream.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_local_height_bound_v1_20261031 import height_fraction, cannot_have_negative_gap
from complete_clearance_cap_paths_v2_20261024 import verify as cap_paths


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','uid','peer','lease']:p.add_argument('--'+k,required=True)
    a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease) and {'building:'+a.uid,'building:'+a.peer}<=set(lease['resources']);assert a.uid!=a.peer;assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[Path(__file__)]
    for name in [a.runtime,a.attributes]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(raw),**{name:np.asarray(attr[key]).reshape(-1,3)[ix]for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    peerrow=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.peer)
    peerattr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.peer)
    peerasset=ROOT/peerrow['candidate']['path'];peerraw=peerasset.read_bytes();assert digest(peerraw)==peerrow['sourceSHA256']==peerattr['sourceSHA256'];refs.append(peerasset)
    pix=np.asarray(peerattr['completeOriginalIndex']).reshape(-1,3)
    peers=dict(original=decode_original_world_triangles(peerraw),**{name:np.asarray(peerattr[key],dtype='<f8').reshape(-1,3)[pix]for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    terrain=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(terrain)>0
    threshold=Fraction(-1,2);summaries=[]
    cache={}
    for name,tri in modes.items():
        assert reservations.owns(lease)
        ground=np.concatenate([terrain,peers[name]]);gxz=ground[:,:,[0,2]];glo=gxz.min(1);ghi=gxz.max(1);maxy=Fraction(float(ground[:,:,1].max()));ground_maxima=[height_fraction(y)for y in ground[:,:,1].max(1)]
        assert len(tri)==row['triangles']
        key=(digest(tri.tobytes()),digest(ground.tobytes()))
        if key in cache:
            prior,document,summary=cache[key]
            assert tri.dtype==prior.dtype and np.array_equal(tri,prior)
            save(out/(name+'.json.gz'),deepcopy(document))
            summaries.append(dict(summary,mode=name))
            print(summaries[-1],flush=True)
            continue
        rows=[];pruned=0;checked=0;candidate_pairs=0;local_pruned=0;height_certificates=[]
        for i,t in enumerate(tri):
            if Fraction(float(t[:,1].min()))-maxy>=threshold:pruned+=1;continue
            txz=t[:,[0,2]];ids=np.flatnonzero(np.all(ghi>=txz.min(0),axis=1)&np.all(glo<=txz.max(0),axis=1));proofs=[]
            source_minimum=height_fraction(t[:,1].min());certified=[]
            for j in ids:
                candidate_pairs+=1
                if cannot_have_negative_gap(source_minimum,ground_maxima[j]):
                    local_pruned+=1;certified.append((int(j),source_minimum-ground_maxima[j]));continue
                proof=verify(t,ground[j]);checked+=1
                if proof['exactClosedHorizontalProjectionsMeet']and Fraction(proof['exactMinimumFiniteColumnGapM'])<threshold:proofs.append(dict(groundFace=int(j),proof=proof))
            if certified:
                height_certificates.append(dict(sourceFace=i,groundFaces=[j for j,_ in certified],exactSourceMinimumY=str(source_minimum),minimumExactGapBoundM=str(min(q for _,q in certified))))
            if not proofs:continue
            cross=np.cross(t[1]-t[0],t[2]-t[0]);norm=float(np.linalg.norm(cross));ratio=abs(float(cross[1]))/norm if norm else None
            v=int(np.argmax(t[:,1]));point=t[v];pis=np.flatnonzero(np.all(glo<=point[[0,2]],axis=1)&np.all(ghi>=point[[0,2]],axis=1));exposed=[]
            for j in pis:
                proof=verify(np.repeat(point[None,:],3,axis=0),ground[j])
                if proof['exactClosedHorizontalProjectionsMeet']:exposed.append(dict(groundFace=int(j),proof=proof))
            rows.append(dict(sourceFace=i,vertices=t.tolist(),absoluteNormalYRatio=ratio,minimumFiniteGapM=str(min(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])for q in proofs)),negativeGroundPairProofs=proofs,highestOriginalVertex=v,highestVertexProofs=exposed,highestVertexAboveEveryOverlappingGroundFace=bool(exposed)and all(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])>0 for q in exposed)))
        assert checked+local_pruned==candidate_pairs
        assert sum(len(r['groundFaces'])for r in height_certificates)==local_pruned
        document=dict(peerUid=a.peer,peerSourceSHA256=peerrow['sourceSHA256'],peerWorldSHA256=digest(peers[name].tobytes()),terrainSHA256=digest(terrain.tobytes()),candidatePairsExamined=candidate_pairs,locallyHeightCertifiedPairs=local_pruned,heightBoundCertificates=height_certificates,sourceWorldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),rows=rows,completeSourceFaces=len(tri),globalHeightBoundPrunedFaces=pruned,finitePairsTested=checked)
        document['completeCompoundClearanceCapPaths']=cap_paths(tri,[r['sourceFace']for r in rows])
        save(out/(name+'.json.gz'),document)
        summaries.append(dict(candidatePairsExamined=candidate_pairs,locallyHeightCertifiedPairs=local_pruned,mode=name,completeSourceFaces=len(tri),globalHeightBoundPrunedFaces=pruned,finitePairsTested=checked,exactAffectedFaces=[r['sourceFace']for r in rows],allAffectedWallLike=all(r['absoluteNormalYRatio']is not None and r['absoluteNormalYRatio']<.25 for r in rows),allAffectedHaveExposedHighestVertex=all(r['highestVertexAboveEveryOverlappingGroundFace']for r in rows)))
        cache[key]=(tri.copy(),deepcopy(document),deepcopy(summaries[-1]))
        print(summaries[-1],flush=True)
    result=dict(uids=[a.uid,a.peer],peerUid=a.peer,peerSourceSHA256=peerrow['sourceSHA256'],sourceSHA256=row['sourceSHA256'],rows=summaries,installationApproved=False,physicalAcceptance=False,architectureReview=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Every source face considered: exact global height bound prunes only definitely clear faces; remaining inclusive finite ground pairs either checked by the unchanged exact finite-column solver or certified by exact source-minimum minus ground-maximum fractions at the unchanged -1/2m threshold; all pruned pair IDs and per-face worst bounds retained. Wall-like normals and exposed vertices are diagnostics, not architectural-role, coverage, support or publication approval.')
    assert reservations.owns(lease)
    assert digest(asset.read_bytes())==row['sourceSHA256'] and digest(peerasset.read_bytes())==peerrow['sourceSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[a.runtime][str(manifest.relative_to(ROOT))];refs.append(manifest)
    for batch,values in pins.items():
        for path in refs:
            key=str(path.relative_to(ROOT))
            if key in values:assert digest(path.read_bytes())==values[key]
    save(out/'summary.json',result);refs.extend([HERE/'complete_clearance_cap_paths_v2_20261024.py',HERE/'exact_local_height_bound_v1_20261031.py',HERE/'test_exact_local_height_bound_v1_20261031.py',HERE/'selected_original_four_world_low_face_context_v2_20261027.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'])
    module('exact_compound_low_face_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-complete-source-lower-face-compound-peer-context',refs,result)


if __name__=='__main__':main()
