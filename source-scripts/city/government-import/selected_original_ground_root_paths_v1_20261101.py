"""Diagnose original shared-edge paths to canonical actual-ground roots.

No source edits, role approval, support approval or installation. Every credited
root is independently replayed against all overlapping drawn ground primitives.
"""
import argparse,sys,uuid,subprocess
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_triangle_pair_column_gap_20261010 import verify as exact_column


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','resources-plan']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--uid',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;planpath=(ROOT/a.resources_plan).resolve()
    assert planpath.is_relative_to(base) and a.batch.startswith('government-xl-') and '/'not in a.batch
    plan=read(planpath);wanted=set(a.uid);assert len(wanted)==len(a.uid) and wanted<=set(plan['uids'])
    resources=set(plan['resources']);assert {'terrain:city/data/terrain.json'}|{'building:'+u for u in wanted}<=resources
    lp=HERE/'local'/a.batch/'reservation.json'
    if not a.owned:
        assert not out.exists()and not lp.parent.exists()
        c=reservations.claim('actual-ground-root-paths-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources and not out.exists()
    refs=[Path(__file__),planpath];pins={}
    def take(batch,path):
        if batch not in pins:_,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    attributes=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest);rows=[];out.mkdir()
    for source in selection['rows']:
        uid=source['uid']
        if uid not in wanted:continue
        assert reservations.owns(lease);asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attrs[uid]['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(asset)
        worlds=represented(attrs[uid],decode_original_world_triangles(asset.read_bytes()));ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(ground)
        glo=ground[:,:,[0,2]].min(1);ghi=ground[:,:,[0,2]].max(1)
        for mode,tri in worlds.items():
            assert reservations.owns(lease);folder=out/uid.split('/')[1]/mode;inputpath=folder/'input.json.gz';rootpath=folder/'canonical-roots.json.gz';pos=tri.reshape(-1).tolist()
            save(inputpath,dict(rows=[dict(uid=uid,position=pos,index=list(range(len(pos)//3)))],podium=ground.tolist()))
            tool=HERE/'original_strict_support_roots_v1_20261024.mjs'
            with(folder/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str(inputpath),str(rootpath)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            roots=read(rootpath);assert roots['inputSHA256']==digest(inputpath.read_bytes()) and roots['uid']==uid
            normal=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0;lo=tri.min(1);hi=tri.max(1)
            def incident(point):
                ix=np.flatnonzero(normal&np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));return [int(i)for i in ix if np.linalg.norm(closest(point,tri[i])-point)<=.001]
            anchors=[];targets=[];replayed=[];nonrendering=[]
            for root in roots['roots']:
                point=np.asarray(root['position']);faces=incident(point)
                if not faces:nonrendering.append(root);continue
                if not root['strictAccepted']:targets.append(dict(witness=root,incidentFaces=faces));continue
                ids=np.flatnonzero(np.all(glo<=point[[0,2]],axis=1)&np.all(ghi>=point[[0,2]],axis=1));proofs=[]
                for j in ids:
                    p=exact_column(np.repeat(point[None,:],3,axis=0),ground[j])
                    if p['exactClosedHorizontalProjectionsMeet']:proofs.append(dict(groundFace=int(j),proof=p))
                assert proofs,'Canonical ground root lacks a finite represented column'
                gap=min(Fraction(p['proof']['exactMinimumFiniteColumnGapM'])for p in proofs);accepted=Fraction(-1,10)<=gap<=1
                replayed.append(dict(sampleIndex=root['sampleIndex'],proofs=proofs,exactMinimumGapM=str(gap),accepted=accepted))
                if accepted:anchors.append(dict(**root,incidentFaces=faces))
                else:targets.append(dict(witness=root,incidentFaces=faces))
            paths=attachment_paths(tri,dict(targets=targets,proof=dict(contacts=[])),[],strict_anchors=anchors)
            result=dict(uid=uid,mode=mode,sourceWorldSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),canonicalRootCandidates=roots['strict']['contacts'],independentlyVerifiedStrictRootCount=len(anchors),independentRootReplay=replayed,canonicalStrictRoots=anchors,nonrenderingOnlyWitnesses=nonrendering,rows=paths,sourceGeometryChanges=0,supportApproved=False,physicalAcceptance=False)
            save(folder/'paths.json.gz',result);refs.extend([inputpath,rootpath,folder/'paths.json.gz',folder/'capture.log'])
            row=dict(uid=uid,mode=mode,sourceSHA256=source['sourceSHA256'],targets=len(paths),strictRoots=len(anchors),finitePaths=sum(p['hasUnrestrictedFiniteAttachment']for p in paths),aboveEndpointCeiling=sum(p.get('riseAboveEndpointsM',0)>0 for p in paths),nonrenderingOnlyWitnesses=len(nonrendering));rows.append(row);print(row,flush=True)
    assert {r['uid']for r in rows}==wanted and reservations.owns(lease)
    for batch,ps in pins.items():
        for path in refs:
            key=str(path.relative_to(ROOT))
            if key in ps:assert digest(path.read_bytes())==ps[key]
    assert digest(manifest.read_bytes())==selection['manifestSHA256']
    refs.extend(HERE/n for n in ['original_strict_support_roots_v1_20261024.mjs','support-contact.mjs','original_face_attachment_minimax_v2_20261024.py','pool_incident_wall_contacts_v1_20261017.py','exact_original_triangle_pair_column_gap_20261010.py','original_assembly_four_world_pair_context_v3_20261101.py','exact_packed_world_geometry_20261009.py'])
    summary=dict(uids=a.uid,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,supportApproved=False,physicalAcceptance=False,installationApproved=False,qualification=__doc__+' Existing canonical[-.1,1]m strict roots are replayed against every overlapping actual drawn primitive, including zero-XZ; same .001m source incidence and original endpoint-height diagnostics. No intercomponent joins invented. Nonrendering-only witnesses retained separately, never credited as paths. All raw strict interface/foundation failures remain unapproved.')
    save(out/'summary.json',summary);module('actual_ground_root_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-drawn-ground-canonical-roots-and-original-shared-edge-path-context',refs,summary)

if __name__=='__main__':main()
