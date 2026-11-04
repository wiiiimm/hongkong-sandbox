"""Rebind unchanged original cap paths to the final ground by exact facet checks."""
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
BATCH=PREFIX+'final-ground-cap-path-revalidation-v1-20261029'
RUNTIME=PREFIX+'seven-upward-floor-runtime-v1-20261029'
ATTRS=PREFIX+'seven-final-ground-attributes-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');runtime=take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz');attrs=take(ATTRS,BASE/ATTRS/'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    out.mkdir();rows=[]
    for model_id in [231013,23220,23759,271344,238142,92881]:
        uid='landsd/'+str(model_id)+':0';source=next(r for r in selection['rows']if r['uid']==uid);captured=next(r for r in runtime['rows']if r['uid']==uid);attr=next(r for r in attrs['rows']if r['uid']==uid);asset=ROOT/source['candidate']['path']
        assert digest(asset.read_bytes())==source['sourceSHA256']==captured['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
        worlds={'original':decode_original_world_triangles(asset.read_bytes())};index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
        assert np.array_equal(worlds['literal'],np.asarray(captured['position']).reshape(-1,3)[np.asarray(captured['index']).reshape(-1,3)])
        ground=np.asarray(captured['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);lo,hi=ground[:,:,[0,2]].min(1),ground[:,:,[0,2]].max(1)
        old_batch=PREFIX+'final-ground-'+str(model_id)+'-0-cap-paths-v1-20261029'
        for mode,triangles in worlds.items():
            old=take(old_batch,BASE/old_batch/(mode+'.json.gz'));assert old['sourceWorldSHA256']==digest(triangles.astype('<f8').tobytes())
            partition=old['completeGroundClearancePartition'];paths=[r for r in partition['paths']if r['hasExactSharedEdgeClearCapPath']]
            assert paths
            normal=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);size=np.linalg.norm(normal,axis=1)
            ids=sorted({i for r in paths for i in r['originalPath']if abs(normal[i,1])>.25*size[i]})
            assert ids and all(normal[r['originalPath'][-1],1]>.25*size[r['originalPath'][-1]]for r in paths)
            faces=[]
            for i in ids:
                tri=triangles[i];xz=tri[:,[0,2]];candidates=np.flatnonzero(np.all(hi>=xz.min(0),axis=1)&np.all(lo<=xz.max(0),axis=1));proofs=[dict(groundFace=int(j),proof=verify(tri,ground[j]))for j in candidates]
                gaps=[Fraction(p['proof']['exactMinimumFiniteColumnGapM'])for p in proofs if p['proof']['exactClosedHorizontalProjectionsMeet']]
                assert gaps
                faces.append(dict(sourceFace=i,inclusiveGroundCandidates=list(map(int,candidates)),proofs=proofs,minimumFiniteGapM=str(min(gaps)),clearanceLimitPassed=min(gaps)>=Fraction(-1,2)))
            record=dict(uid=uid,mode=mode,sourceSHA256=source['sourceSHA256'],sourceWorldSHA256=old['sourceWorldSHA256'],oldGroundSHA256=old['completeDrawnGroundSHA256'],finalGroundSHA256=digest(ground.tobytes()),completeFinalGroundFaces=len(ground),unchangedPriorPaths=paths,nonWallPathFacets=faces,qualification='Topology/positive source contacts are unchanged and authenticated by the prior exact source-world hash. Every non-wall facet in every previously passing path is checked against all inclusive final drawn-ground candidates; no monotonic-height assumption or changed clearance threshold.')
            name=str(model_id)+'-'+mode+'.json.gz';save(out/name,record);row=dict(uid=uid,mode=mode,priorPassingPaths=len(paths),recheckedNonWallPathFacets=len(ids),allPathConnectorsAndCapsStillClear=all(r['clearanceLimitPassed']for r in faces),proof=name);rows.append(row);print(row,flush=True)
    result=dict(uids=sorted({r['uid']for r in rows}),rows=rows,allPriorPassingPathsRetainFinalGroundEligibility=all(r['allPathConnectorsAndCapsStillClear']for r in rows),sourceGeometryChanges=0,physicalAcceptance=False,groundRootCredit=False,installationApproved=False,publication=False,qualification='Revalidation of previously passing source-only cap paths against final exact ground. Existing partial-clearance, remaining-role, ordinary-anchor, whole-source identity/height/neighbour/browser and publication gates stay independent. No new topology, model edits, ground edits or unconditional wall-role approval.')
    save(out/'summary.json',result)
    module('sha_tin_cap_final_revalidation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-original-cap-path-final-drawn-ground-exact-revalidation',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
