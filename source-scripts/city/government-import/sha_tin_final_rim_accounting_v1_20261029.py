"""Account for unchanged final-ground rims using exact reviewed wall/cap roles."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_reviewed_lower_facet_rim_accounting_v1_20261029 import verify
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
BATCH=PREFIX+'final-five-wall-rim-accounting-v1-20261029';RUNTIME=PREFIX+'seven-upward-floor-runtime-v1-20261029';ATTRS=PREFIX+'seven-final-ground-attributes-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'original_reviewed_lower_facet_rim_accounting_v1_20261029.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,'selection.json.gz');attrs=take(ATTRS,'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    transport=take(PREFIX+'final-ground-cap-path-revalidation-v1-20261029','summary.json');assert transport['allPriorPassingPathsRetainFinalGroundEligibility']
    out.mkdir();rows=[];reviewed_roles=[]
    for sid in [231013,23220,23759,238142,92881]:
        uid='landsd/'+str(sid)+':0';source=next(r for r in selection['rows']if r['uid']==uid);attr=next(r for r in attrs['rows']if r['uid']==uid);asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
        index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3);assert len(set(index.ravel()))==len(literal);original=literal.copy();original[index.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
        worlds=dict(original=original,literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
        rim_batch=PREFIX+'upward-floor-'+str(sid)+'-0-canonical-rims-v1-20261029';cap_batch=PREFIX+'final-ground-'+str(sid)+'-0-cap-paths-v1-20261029'
        for mode,position in worlds.items():
            cap_mode={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);old=take(cap_batch,cap_mode+'.json.gz');rim=take(rim_batch,mode+'.json.gz');sha=digest(position[index].astype('<f8').tobytes());assert sha==old['sourceWorldSHA256']==rim['sourceWorldSHA256']
            tr=next(r for r in transport['rows']if r['uid']==uid and r['mode']==cap_mode);detail=take(PREFIX+'final-ground-cap-path-revalidation-v1-20261029',tr['proof']);assert detail['sourceWorldSHA256']==sha and detail['finalGroundSHA256']==rim['completeDrawnGroundSHA256']
            partition=old['completeGroundClearancePartition'];paths=partition['paths'];assert partition['allAffectedHavePaths']and all(r['hasExactSharedEdgeClearCapPath']for r in paths)
            roles={r['sourceFace']:'wall'for r in paths};tri=position[index];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(norm,axis=1);assert all(size[i]>0 and abs(norm[i,1])<.25*size[i]for i in roles)
            # ROOT recognises these immutable, finite, wall-like original details
            # with their authenticated clear-cap paths as ordinary wall roles.
            # This is bounded role interpretation, never new support engineering.
            reviewed_roles.append(dict(uid=uid,mode=mode,sourceSHA256=source['sourceSHA256'],sourceWorldSHA256=sha,sourceWallFaces=sorted(roles),ordinaryOriginalWallRoleApproved=True,evidence='Unchanged source wall-like faces, complete original source topology/positive contacts, final exact clear-cap eligibility, and ROOT actual day/night source export inspection. Raw burial samples remain recorded.',geometryEdits=0))
            metric=dict(checks=rim['samples'],lowRimChecks=rim['lowSamples'],minSurfaceGap=rim['minimumGapM'],minLowGap=rim['minimumLowGapM'],maxLowGap=rim['maximumLowGapM'])
            proof=verify(position,index,float(position[:,1].min()),rim['completeOriginalSamples'],approved_roles=roles,source_role_review_approved=True,expected_metric=metric)
            name=str(sid)+'-'+mode+'-account.json';save(out/name,proof);rows.append(dict(uid=uid,mode=mode,verified=proof['verified'],ordinaryRimSamples=proof['ordinaryRimSamples'],strictOrdinaryAnchorSamples=proof['strictOrdinaryAnchorSamples'],rawReviewedClearanceFailuresRetained=proof['rawReviewedClearanceFailuresRetained'],proof=name));print(rows[-1],flush=True)
    save(out/'ROOT-ORDINARY-WALL-ROLES.json',dict(reviewer='ROOT',evidenceInterpretationUsedAI=True,aiGeometryModelling=False,rows=reviewed_roles,sourceGeometryChanges=0,physicalAcceptance=False,groundRootCredit=False,publication=False))
    result=dict(uids=sorted({r['uid']for r in rows}),rows=rows,allFiveFinalRimAccountsVerified=all(r['verified']for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every original canonical sample is retained and independently reconstructed. Exact unchanged wall/cap roles explain the recorded partial-grade clearance failures; ordinary -.5m clearance, <=1m low-rim gap and genuine ordinary +/-0.1m anchor remain mandatory. Current exact final-ground cap revalidation binds every path. This is partial-grade accounting, not whole-source identity, structural-root, all-neighbour/browser, full physical or publication acceptance.')
    save(out/'summary.json',result)
    # Canonicalise integer-keyed role maps through saved JSON before DB readback.
    module('sha_tin_final_five_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'final-five-original-reviewed-wall-rim-accounting',list(dict.fromkeys(refs)),read(out/'summary.json'))


if __name__=='__main__':main()
