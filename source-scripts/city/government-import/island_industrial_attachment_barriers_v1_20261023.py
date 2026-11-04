"""Measure exact original attachment barriers and a retained tiny roof component."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from finite_surface_minimax_paths_v1_20261023 import adjacency,minimum_barrier
from pool_incident_wall_contacts_v1_20261017 import closest


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-original-attachment-barriers-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';selected=take(runtime,'selection.json.gz')['rows'];source=next(r for r in selected if r['uid']=='landsd/20270:0');asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);t=decode_original_world_triangles(asset.read_bytes())
    prior='government-xl-island-industrial-tower-main-podium-fourworld-paths-v1-20261023';before=take(prior,'original.json.gz');assert digest(t.tobytes())==before['sourceWorldSHA256'];target=[r for r in before['rows']if not r['verifiedPath']];assert len(target)==52
    # This file is explicitly only a nomination from an interrupted diagnostic;
    # every selected pair below receives a new exact source-geometry replay.
    nomination=base/'government-xl-island-industrial-joined-source-fourworld-paths-v1-20261023/selected-original-bridges.json.gz';refs.append(nomination);nominated=read(nomination);joins=[];replays=[]
    for number,c in enumerate(nominated):
        old=c['originalContact'];a,b=old['sourceFaceA'],old['sourceFaceB'];proof=exact_component_contacts_with_primitives(t,[a],t,[b],maximum_pairs=1);assert proof['allPairsExamined'];replays.append(dict(sourceFaces=[a,b],proof=proof))
        for p in proof['contacts']:
            if p['dimension']>0 and p['primitiveDimensions']==[2,2]:joins.append(dict(p,points=[[float(Fraction(v))for v in q]for q in p['exactPoints']]))
        if number%1000==0:print(dict(replayed=number,total=len(nominated)),flush=True)
    save(out/'exact-replayed-source-joins.json.gz',replays);adj,valid=adjacency(t,joins);endpoints=[]
    for c in before['exactContacts']['contacts']:
        if c['dimension']<=0 or c['sourcePrimitiveDimensionA']!=2 or c['sourcePrimitiveDimensionB']!=2:continue
        points=np.array([[float(Fraction(v))for v in p]for p in c['exactPoints']])
        for point in [*points,points.mean(0)]:endpoints.append(dict(sourceFace=c['sourceFaceA'],supportFace=c['sourceFaceB'],point=point.tolist(),exactContact=c))
    rows=[]
    for k,row in enumerate(target):
        proof=minimum_barrier(t,adj,valid,row['witness']['position'],row['incidentFaces'],endpoints);rows.append(dict(witness=row['witness'],incidentFaces=row['incidentFaces'],minimumBarrierPath=proof));print(dict(target=k,connected=proof is not None,extraHeightM=proof['minimumExcessOverOwnEndpointsM']if proof else None),flush=True)
    save(out/'measured-paths.json.gz',dict(sourceWorldSHA256=before['sourceWorldSHA256'],supportWorldSHA256=before['supportWorldSHA256'],rows=rows))
    connectivity=take('government-xl-island-industrial-contact-connectivity-v1-20261023','landsd-20270-0.json');assert connectivity['sourceSHA256']==source['sourceSHA256'];clusters=connectivity['clusters'];main=max(clusters,key=lambda c:c['faceCount']);secondary=[c for c in clusters if c is not main];tiny=[];mainids=np.asarray(main['faceIds']);body=t[mainids];low,high=body.min(1),body.max(1)
    for c in secondary:
        points=t[c['faceIds']].reshape(-1,3);qlo,qhi=points.min(0),points.max(0);candidates=np.flatnonzero(np.all(high>=qlo-.001,axis=1)&np.all(low<=qhi+.001,axis=1));best=None
        for index in candidates:
            face=body[index];bound=max(float(np.linalg.norm(closest(q,face)-q))for q in points)
            if best is None or bound<best['convexDistanceUpperBoundM']:best=dict(mainFace=int(mainids[index]),convexDistanceUpperBoundM=bound)
        tri=t[c['faceIds']];area=float(np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1).sum()/2);tiny.append(dict(faceIds=c['faceIds'],diameterOfAABBMetres=float(np.linalg.norm(qhi-qlo)),renderedAreaM2=area,commonMainTriangleProximity=best,qualification='Maximum vertex distance to one common convex main triangle bounds every point of the convex secondary triangles. Proximity is not exact contact or structural support approval; no geometry removal.'))
    result=dict(uids=['landsd/20270:0','landsd/159422:0'],targets=len(rows),connectedTargets=sum(r['minimumBarrierPath']is not None for r in rows),strictEndpointHeightPassed=sum(r['minimumBarrierPath']is not None and r['minimumBarrierPath']['strictOwnEndpointHeightPassed']for r in rows),minimumExtraHeightM=min([r['minimumBarrierPath']['minimumExcessOverOwnEndpointsM']for r in rows if r['minimumBarrierPath']],default=None),maximumExtraHeightM=max([r['minimumBarrierPath']['minimumExcessOverOwnEndpointsM']for r in rows if r['minimumBarrierPath']],default=None),secondaryComponents=tiny,nonrenderingFacesRetained=connectivity['excludedNonrenderingFaces'],installationApproved=False,sourceGeometryChanges=0,qualification='Original-coordinate diagnostic only, fresh exact positive-dimensional nondegenerate source joins and finite convex surface paths. Nonrendering and point-only contacts provide no adjacency. Raw endpoint-height failures remain; uphill paths do not receive automatic architectural/support approval. Other coordinate worlds, foreign/identity/collision/runtime/browser and publication still required.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['finite_surface_minimax_paths_v1_20261023.py','test_finite_surface_minimax_paths_v1_20261023.py','exact_original_primitive_contacts_v1.py','exact_packed_world_geometry_20261009.py','pool_incident_wall_contacts_v1_20261017.py']);module('barrier_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-finite-attachment-height-barrier-diagnostic',refs,result);print(result,flush=True)

if __name__=='__main__':main()
