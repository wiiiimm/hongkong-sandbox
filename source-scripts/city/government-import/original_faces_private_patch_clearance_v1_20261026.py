"""Conditional finite clearance of explicit original faces against a private terrain patch.

Does not resolve overlap with installed terrain or grant any publication credit.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime','attributes','low-faces','patch','uid']:p.add_argument('--'+name,required=True)
    p.add_argument('--face',type=int,action='append',required=True);a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={};receipts={}
    def take(batch,path):
        if batch not in pins:receipts[batch],pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selected['rows']if r['uid']==a.uid)
    attrs=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attr=next(r for r in attrs['rows']if r['uid']==a.uid)
    low=take(a.low_faces,base/a.low_faces/'summary.json');assert low['sourceSHA256']==row['sourceSHA256']==attr['sourceSHA256']
    ids=a.face;assert ids==sorted(set(ids)) and set(ids)<=set(low['rows'][0]['exactAffectedFaces'])
    patchsummary=take(a.patch,base/a.patch/'summary.json');assert patchsummary['status']=='private-terrain-validator-passed'
    candidate=receipts[a.patch]['candidate'];path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256'];refs.append(path);terrain=read(path)
    assert terrain.get('nativeMesh')and not terrain.get('patches');mesh=terrain['nativeMesh']
    ground=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
    polygons=shapely.polygons(ground[:,:,[0,2]]);area=shapely.union_all(polygons);glo=ground[:,:,[0,2]].min(1);ghi=ground[:,:,[0,2]].max(1)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]});results=[]
    for mode,tri in worlds.items():
        old=take(a.low_faces,base/a.low_faces/(mode+'.json.gz'));assert old['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())
        details=[]
        for index in ids:
            face=tri[index];assert np.cross(face[1]-face[0],face[2]-face[0])[1]>0
            footprint=shapely.Polygon(face[:,[0,2]]);assert footprint.area>0
            assert footprint.difference(area).area==0,'Candidate does not continuously cover selected original face'
            xz=face[:,[0,2]];near=np.flatnonzero(np.all(ghi>=xz.min(0),axis=1)&np.all(glo<=xz.max(0),axis=1));proofs=[]
            for j in near:
                proof=verify(face,ground[j])
                if proof['exactClosedHorizontalProjectionsMeet']:proofs.append(dict(groundFace=int(j),proof=proof))
            assert proofs
            minimum=min(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])for q in proofs)
            details.append(dict(sourceFace=index,minimumFiniteGapM=str(minimum),clearsExistingHalfMetreGate=minimum>=Fraction(-1,2),proofs=proofs))
        save(out/(mode+'.json.gz'),dict(sourceWorldSHA256=old['sourceWorldSHA256'],candidateGroundSHA256=digest(ground.tobytes()),rows=details))
        results.append(dict(mode=mode,faces=[dict(sourceFace=r['sourceFace'],minimumFiniteGapM=r['minimumFiniteGapM'],clearsExistingHalfMetreGate=r['clearsExistingHalfMetreGate'])for r in details]));print(results[-1],flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=sorted(set([a.uid,*receipts[a.patch]['uids']])),uid=a.uid,sourceSHA256=row['sourceSHA256'],rows=results,
                candidateTerrainSHA256=candidate['sha256'],sourceGeometryChanges=0,sourcePoseChanges=0,terrainInstalled=False,
                installedTerrainOverlapResolved=False,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Every selected original face continuously covered by private candidate terrain and exact finite-column comparisons in all four source representations. Conditional on resolving the installed-terrain overlap correctly; not the actual current scene, a retained-terrain proof, a full model foundation pass, source-role or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'])
    module('private_patch_faces_clearance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'conditional-original-upward-faces-private-terrain-clearance',refs,result)


if __name__=='__main__':main()
