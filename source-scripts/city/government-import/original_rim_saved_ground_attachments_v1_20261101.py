"""Trace retained support warnings to actual saved finite source/ground contacts.

Diagnostic only. Reuses unchanged attachment incidence and endpoint mathematics;
no new source edges, geometric roots, tolerance or physical acceptance.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--uid',action='append',required=True);p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease))
    assert set(a.uid)<={'landsd/252556:0','landsd/252558:0'}and len(a.uid)==len(set(a.uid))and reservations.owns(lease)
    for uid in a.uid:
        key=uid.split('/')[1].split(':')[0];batch=P+key+'-saved-ground-attachments-v1-20261101';out=BASE/batch;assert not out.exists()and'building:'+uid in lease['resources'];refs=[Path(__file__)];pins={}
        def take(name,file,external=None):
            if name not in pins:_,pins[name]=authenticate(BASE/name);refs.append(BASE/name/'result.json')
            path=external if external is not None else BASE/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
        rt=P+'twenty-authentic-tin-runtime-v1-20261101';at=P+'twenty-original-attributes-v1-20261101';previous=P+key+'-finite-original-attachments-v1-20261101';strict=P+key+'-original-owner-support-v1-20261101';grade=P+key+'-twenty-source-ground-contacts-v1-20261101'
        source=next(r for r in take(rt,'selection.json.gz')['rows']if r['uid']==uid);attr=next(r for r in take(at,'attributes.json.gz')['rows']if r['uid']==uid);g=next(r for r in take(rt,'',HERE/'local'/rt/'runtime-geometry.json.gz')['rows']if r['uid']==uid);old=take(previous,'summary.json');direct=take(strict,'summary.json');take(grade,'summary.json')
        assert old['sourceSHA256ByUid'][uid]==source['sourceSHA256']==attr['sourceSHA256']==g['sourceSHA256']
        ap=BASE/at/'attributes.json.gz';assert pins[previous][str(ap.relative_to(ROOT))]==digest(ap.read_bytes())
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);worlds=represented(attr,decode_original_world_triangles(asset.read_bytes()));ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);rows=[]
        decoder=HERE/'exact_packed_world_geometry_20261009.py';assert pins[previous][str(decoder.relative_to(ROOT))]==digest(decoder.read_bytes())
        for mode,tri in worlds.items():
            assert reservations.owns(lease)
            evidence=take(grade,mode+'.json.gz');assert evidence['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())and evidence['completeGroundSHA256']==digest(ground.tobytes())and evidence['sourceFacesOmitted']==evidence['groundFacesOmitted']==0
            finite=evidence['proof'];assert finite['allPairsExamined']and finite['sourceFacesOmitted']==0
            contacts=[dict(c,peerUid='current-drawn-ground')for c in finite['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
            bound=next(r for r in direct['rows']if r['mode']==mode);assert bound['sourceWorldSHA256ByUid'][uid]==evidence['sourceWorldSHA256']
            valid=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0;lo,hi=tri.min(1),tri.max(1);targets=[]
            for witness in bound['support']['unresolved']:
                point=np.asarray(witness['position']);candidates=np.flatnonzero(valid&np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));incident=[int(i)for i in candidates if np.linalg.norm(closest(point,tri[i])-point)<=.001];assert incident;targets.append(dict(witness=witness,incidentFaces=incident))
            selfproof=take(previous,mode+'-complete-self-contacts.json.gz');assert selfproof['allPairsExamined']and selfproof['sourceFacesOmitted']==0
            joins=[dict(c,primitiveDimensions=[2,2])for c in selfproof['contacts']if c['sourceFaceA']<c['sourceFaceB']and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
            paths=attachment_paths(tri,dict(targets=targets,proof=dict(contacts=contacts)),joins)
            assert [r['witness']for r in paths]==bound['support']['unresolved'];save(out/(mode+'.json.gz'),dict(rows=paths,sourceWorldSHA256=evidence['sourceWorldSHA256'],completeGroundSHA256=evidence['completeGroundSHA256']))
            rows.append(dict(mode=mode,witnesses=len(paths),hasFiniteGroundAttachment=sum(r['hasUnrestrictedFiniteAttachment']for r in paths),passesExistingEndpointHeight=sum(r.get('passesExistingEndpointHeight',False)for r in paths),groundContactTerminals=len(contacts),newFiniteContactComputations=0))
        result=dict(uids=[uid],sourceSHA256=source['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Every raw warning remains. Complete current source/ground contact arrays and prior complete self contacts are authenticated; no contacts recomputed, joins invented or original endpoint/residual limits changed. Ground contact roles and complete source/scene applicability require separate review.')
        assert reservations.owns(lease);save(out/'summary.json',result);refs.extend([decoder,HERE/'original_assembly_four_world_pair_context_v3_20261101.py',HERE/'original_face_attachment_minimax_v2_20261024.py',HERE/'pool_incident_wall_contacts_v1_20261017.py']);module('rim_saved_ground_attachment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'original-rim-to-complete-saved-current-ground-contact-paths',list(dict.fromkeys(refs)),result);print(dict(uid=uid,rows=rows),flush=True)
if __name__=='__main__':main()
