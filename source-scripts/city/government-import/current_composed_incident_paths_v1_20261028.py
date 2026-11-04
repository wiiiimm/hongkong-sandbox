"""Bounded exact incident-face paths for current composed-scene warnings.

Only nominated sources and their exact current warning positions are processed.
No geometry edits, new joins, support limits or architectural approvals.
"""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_face_attachment_minimax_v2_20261024 import attachment_paths

BASE=ROOT/'docs/astra-city/government-import'
CURRENT='government-xl-elegant-garden-final-sixteen-composed-support-v1-20261028'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True)
    p.add_argument('--uid',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out=BASE/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json'
    assert not out.exists() and len(set(a.uid))==len(a.uid)
    resourcepath=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json'
    resources=set(read(resourcepath)['resources']);assert {'building:'+u for u in a.uid}<=resources
    if not a.owned:
        assert not local.exists()
        claim=reservations.claim('current-composed-incident-paths-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600)
        assert claim['ok'];return execute_reserved(claim['reservation'],leasepath,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(leasepath);assert reservations.owns(lease) and resources<=set(lease['resources'])
    _,pins=authenticate(BASE/CURRENT);refs=[Path(__file__),resourcepath,BASE/CURRENT/'result.json']
    def take(name):
        path=BASE/CURRENT/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    summary=take('summary.json');inputs=take('input.json.gz');previous=take('contacts.json.gz')
    assert set(a.uid)<=set(summary['uids']);rows=[]
    def tri(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    for uid in a.uid:
        for mode in ['original','literal','leftF32','balancedF32']:
            assert reservations.owns(lease)
            data=next(r for r in inputs['rows'] if r['uid']==uid and r['mode']==mode)
            prior=next(r for r in previous['rows'] if r['uid']==uid and r['mode']==mode)
            source,support=tri(data['source']),tri(data['support'])
            assert digest(source.tobytes())==data['sourceWorldSHA256']==prior['sourceWorldSHA256']
            assert digest(support.tobytes())==data['supportWorldSHA256']==prior['supportWorldSHA256']
            witnesses=prior['rawInterface']['unresolved'];assert witnesses and prior['rawInterface']['maximumEmbeddingM']==.5
            lo,hi=source.min(1),source.max(1)
            renderable=np.linalg.norm(np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0]),axis=1)>0
            targets=[];unmapped=[];allids=set()
            for witness in witnesses:
                point=np.asarray(witness['position']);broad=np.flatnonzero(renderable & np.all(lo<=point+.001,axis=1) & np.all(hi>=point-.001,axis=1))
                ids=[int(i) for i in broad if np.linalg.norm(closest(point,source[i])-point)<=.001]
                target=dict(witness=witness,incidentFaces=ids)
                if ids:targets.append(target);allids.update(ids)
                else:unmapped.append(target)
            proof=exact_finite_contacts(source,sorted(allids),support,list(range(len(support)))) if allids else dict(contacts=[])
            paths=attachment_paths(source,dict(targets=targets,proof=proof),[]) if targets else []
            assert [r['witness'] for r in paths]==[r['witness'] for r in targets]
            result=dict(uid=uid,mode=mode,currentWarnings=len(witnesses),incidentFaces=len(allids),
                mappedWitnesses=len(targets),unmappedWitnesses=len(unmapped),
                endpointBoundedPaths=sum(r.get('passesExistingEndpointHeight',False) for r in paths),
                sourceWorldSHA256=data['sourceWorldSHA256'],supportWorldSHA256=data['supportWorldSHA256'])
            save(out/(uid.split('/')[1]+'-'+mode+'.json.gz'),dict(**result,paths=paths,unmapped=unmapped,proof=proof))
            rows.append(result);print(result,flush=True)
    result=dict(uids=a.uid,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,
        physicalSupportAccepted=False,identityAccepted=False,installationApproved=False,
        qualification='Bounded incident-face contact search against every complete support facet in the authenticated composed scene. Every current witness retained, including unmapped/degenerate cases. Exact original-edge minimax paths use unchanged finite contacts, own endpoint-height and 0.001m residual gates. No extra source joins or remote source faces are searched as terminals; a missing path here is not an impossibility proof. Contacts and paths do not approve architectural roles, support roots/cycles, collision or publication.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['pool_incident_wall_contacts_v1_20261017.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','original_face_attachment_minimax_v2_20261024.py'])
    assert reservations.owns(lease)
    module('current_composed_incident_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'bounded-current-composed-warning-incident-face-paths',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
