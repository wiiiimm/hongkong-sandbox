"""Rebind accepted source-wall paths to exact current warnings, never approve placement.

Reuse is permitted only for identical complete source/podium arrays and warning
records. Every saved segment and finite terminal contact is independently checked.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

BASE=ROOT/'docs/astra-city/government-import'
CURRENT='government-xl-elegant-garden-final-sixteen-composed-support-v1-20261028'
OLD='government-xl-elegant-garden-block2-four-world-support-v1-20261027'
PATHS='government-xl-elegant-garden-seven-witness-paths-v1-20261027'
ROLE='government-xl-elegant-garden-four-wall-role-v1-20261027'
UID,SUPPORT='landsd/173532:0','landsd/236170:0'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out=BASE/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json'
    assert not out.exists()
    resourcepath=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json'
    resources=set(read(resourcepath)['resources'])
    if not a.owned:
        assert not local.exists()
        claim=reservations.claim('elegant-current-source-wall-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'],leasepath,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(leasepath);assert reservations.owns(lease) and resources<=set(lease['resources'])
    refs=[Path(__file__),resourcepath];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    summary=take(CURRENT,'summary.json');inputs=take(CURRENT,'input.json.gz');contacts=take(CURRENT,'contacts.json.gz')
    old=take(OLD,'summary.json');role=take(ROLE,'ROOT-SOURCE-WALL-ROLE.json')
    assert role['sourceWallRoleAccepted'] and role['all28PathsWithinExistingEndpointHeight']
    assert {u:summary['sourceScopes'][u]['sourceSHA256'] for u in [UID,SUPPORT]}==role['sourceSHA256ByUid']==old['sourceSHA256ByUid']
    sourcepart=next(x for x in summary['supportRosters'][UID] if x.get('uid')==SUPPORT)
    def triangles(g):
        return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    rows=[]
    for mode in ['original','literal','leftF32','balancedF32']:
        assert reservations.owns(lease)
        data=next(r for r in inputs['rows'] if r['uid']==UID and r['mode']==mode)
        current=next(r for r in contacts['rows'] if r['uid']==UID and r['mode']==mode)
        prior=next(r for r in old['rows'] if r['mode']==mode)
        paths=take(PATHS,mode+'.json.gz')['rows']
        source=triangles(data['source']);support=triangles(data['support'])[slice(*sourcepart['sourceFaceRange'])]
        assert digest(source.tobytes())==data['sourceWorldSHA256']==current['sourceWorldSHA256']==prior['sourceWorldSHA256ByUid'][UID]
        assert digest(support.tobytes())==prior['sourceWorldSHA256ByUid'][SUPPORT]
        warnings=current['rawInterface']['unresolved']
        assert warnings==prior['support']['unresolved']==[r['witness'] for r in paths],'Current warnings differ; recompute current paths'
        assert len(paths)==7 and current['rawInterface']['maximumEmbeddingM']==.5
        checked=[]
        for path in paths:
            assert path['hasUnrestrictedFiniteAttachment'] and path['passesExistingEndpointHeight'] and path['riseAboveEndpointsM']==0
            ids=path['faces'];points=np.asarray(path['continuousPath'],dtype='<f8')
            assert len(points)==len(ids)+1 and set(ids)<=set(role['sourceFaces'])
            assert np.array_equal(points[0],path['witness']['position'])
            residual=max(float(np.linalg.norm(closest(q,source[f])-q)) for i,f in enumerate(ids) for q in points[i:i+2])
            assert residual<=.001 and points[:,1].max()<=path['endpointHeightCeilingM']+1e-9
            contact=path['terminal']['contact'];assert ids[-1]==contact['sourceFaceA']
            proof=exact_finite_contacts(source,[contact['sourceFaceA']],support,[contact['sourceFaceB']])
            keys=['dimension','sourcePrimitiveDimensionA','sourcePrimitiveDimensionB','exactPoints']
            assert any(all(c[k]==contact[k] for k in keys) for c in proof['contacts'])
            assert contact['dimension']>0 and contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2
            assert np.linalg.norm(closest(points[-1],support[contact['sourceFaceB']])-points[-1])<=.001
            checked.append(dict(witness=path['witness'],faces=ids,maximumResidualM=residual,exactTerminalContactRechecked=True))
        save(out/(mode+'.json.gz'),dict(mode=mode,rows=checked,sourceWorldSHA256=data['sourceWorldSHA256'],podiumWorldSHA256=digest(support.tobytes())))
        rows.append(dict(mode=mode,exactCurrentWarnings=len(warnings),verifiedExistingPaths=len(checked)))
        print(rows[-1],flush=True)
    result=dict(uids=[UID,SUPPORT],rows=rows,sourceWallRoleRebound=True,sourceGeometryChanges=0,
        sourcePoseChanges=0,aiGeometryModelling=False,physicalSupportAccepted=False,currentMapPlacementAccepted=False,
        installationApproved=False,qualification='Exact current warning-list equality and complete source/podium-array equality, followed by fresh finite terminal intersection and every saved path segment revalidation under unchanged endpoint-height/0.001m gates. Reuses the already inspected four-wall source interpretation only; whole assembly, identity, root, collision, visual and publication approval remain separate.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['pool_incident_wall_contacts_v1_20261017.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py'])
    assert reservations.owns(lease)
    module('current_elegant_wall_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-witness-and-source-bound-existing-wall-path-revalidation',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
