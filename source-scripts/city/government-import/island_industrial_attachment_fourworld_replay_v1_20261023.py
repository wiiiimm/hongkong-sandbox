"""Fresh finite attachment-path replay in every actual source coordinate world."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from pool_incident_wall_contacts_v1_20261017 import closest


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-attachment-fourworld-replay-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    barrier='government-xl-island-industrial-original-attachment-barriers-v1-20261023';measured=take(barrier,'measured-paths.json.gz');report=take(barrier,'summary.json');assert report['targets']==report['connectedTargets']==52
    prior='government-xl-island-industrial-tower-main-podium-fourworld-paths-v1-20261023';original=take(prior,'original.json.gz');indices=[]
    for r in measured['rows']:
        found=[i for i,old in enumerate(original['rows'])if old['witness']==r['witness']];assert len(found)==1;indices.append(found[0])
    runtime='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';selected=take(runtime,'selection.json.gz')['rows'];attrs=take('government-xl-island-cheong-shing-four-original-attributes-v1-20261023','attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']};uids=['landsd/20270:0','landsd/159422:0'];worlds={}
    for uid in uids:
        r=next(r for r in selected if r['uid']==uid);asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']==attrs[uid]['sourceSHA256'];refs.append(asset);worlds[uid]={'original':decode_original_world_triangles(raw)};ix=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3)
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(attrs[uid][field],dtype='<f8').reshape(-1,3)[ix]
    summaries=[];paircache={}
    for mode in ['original','literal','leftF32','balancedF32']:
        t=worlds[uids[0]][mode];support=worlds[uids[1]][mode];before=take(prior,mode+'.json.gz');assert digest(t.tobytes())==before['sourceWorldSHA256']and digest(support.tobytes())==before['supportWorldSHA256'];rows=[]
        def contact(a,b,old,supported=False):
            key=(digest(t[[a]].tobytes()),digest((support if supported else t)[[b]].tobytes()),a,b,supported)
            if key not in paircache:paircache[key]=exact_component_contacts_with_primitives(t,[a],support if supported else t,[b],maximum_pairs=1)
            proof=paircache[key];assert proof['allPairsExamined'];valid=[p for p in proof['contacts']if p['dimension']>0 and p['primitiveDimensions']==[2,2]];assert valid,'Finite positive attachment disappeared in current world'
            candidates=[]
            for p in valid:
                q=np.array([[float(Fraction(v))for v in x]for x in p['exactPoints']])
                candidates.extend((x,p)for x in [*q,q.mean(0)])
            point,certificate=min(candidates,key=lambda x:float(np.linalg.norm(x[0]-old)));assert np.linalg.norm(point-old)<=.001
            return point,certificate
        for i,record in zip(indices,measured['rows']):
            old=record['minimumBarrierPath'];current=before['rows'][i];assert not current['verifiedPath'];ids=old['faces'];assert ids[0]in current['incidentFaces'];normals=np.cross(t[ids,1]-t[ids,0],t[ids,2]-t[ids,0]);assert (np.linalg.norm(normals,axis=1)>0).all()
            start=np.asarray(current['witness']['position']);points=[start];joins=[]
            for j,(a,b)in enumerate(zip(ids,ids[1:])):
                p,c=contact(a,b,np.asarray(old['path'][j+1]));points.append(p);joins.append(c)
            endpoint=old['sourceContact'];end,c=contact(ids[-1],endpoint['supportFace'],np.asarray(old['path'][-1]),True);points.append(end)
            residual=max(float(np.linalg.norm(closest(p,t[f])-p))for k,f in enumerate(ids)for p in points[k:k+2]);residual=max(residual,float(np.linalg.norm(closest(end,support[endpoint['supportFace']])-end)));assert residual<=.001
            maximum=max(float(p[1])for p in points);ceiling=max(float(start[1]),float(end[1]));extra=maximum-ceiling;assert extra>=-1e-9
            rows.append(dict(witness=current['witness'],sourceFaces=ids,continuousPath=[p.tolist()for p in points],exactInternalJoins=joins,exactSupportContact=c,maximumSurfaceResidualM=residual,maximumPathHeightM=maximum,ownEndpointHeightM=ceiling,excessOverOwnEndpointsM=extra,strictEndpointHeightPassed=extra<=1e-9,withinHalfMetreDiagnosticBound=extra<=.5,installationApproved=False))
        micro=[]
        for component in report['secondaryComponents']:
            face=component['commonMainTriangleProximity']['mainFace'];q=t[component['faceIds']].reshape(-1,3);upper=max(float(np.linalg.norm(closest(p,t[face])-p))for p in q);diameter=float(np.linalg.norm(q.max(0)-q.min(0)));assert upper<=.001 and diameter<=.01
            micro.append(dict(faceIds=component['faceIds'],commonMainFace=face,convexWholeComponentDistanceUpperBoundM=upper,diameterOfAABBMetres=diameter,exactContactClaimed=False,sourceGeometryRemoved=False))
        save(out/(mode+'.json.gz'),dict(mode=mode,sourceWorldSHA256=before['sourceWorldSHA256'],supportWorldSHA256=before['supportWorldSHA256'],rows=rows,secondaryComponentProximity=micro));summary=dict(mode=mode,paths=len(rows),freshFinitePaths=len(rows),strictEndpointHeightPassed=sum(r['strictEndpointHeightPassed']for r in rows),maximumMeasuredExcessM=max(r['excessOverOwnEndpointsM']for r in rows),maximumSurfaceResidualM=max(r['maximumSurfaceResidualM']for r in rows),allWithinHalfMetreDiagnosticBound=all(r['withinHalfMetreDiagnosticBound']for r in rows),secondaryComponents=micro);summaries.append(summary);print(summary,flush=True)
    result=dict(uids=uids,rows=summaries,sourceGeometryChanges=0,installationApproved=False,physicalSupportAccepted=False,qualification='Every one of52previous strict failures replayed using fresh exact positive-dimensional original intersections in all4coordinate worlds, no nonrendering path credit. Uphill attachment measurements remain separate from strict endpoint-height approval. Tiny retained source component has one common convex main-triangle proximity bound, not exact contact. Half-metre bound is diagnostic only; no generic guard, source-internal embedding, foreign overlap, architectural or publication exception granted.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py','pool_incident_wall_contacts_v1_20261017.py']);module('attachment_fourworld_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fresh-fourworld-original-finite-uphill-attachment-replay',refs,result)

if __name__=='__main__':main()
