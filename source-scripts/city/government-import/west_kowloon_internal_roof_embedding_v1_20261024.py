"""Attribute source-pair embedding warnings separately from actual terrain burial."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives


def finite_surface(t):
    p=shapely.polygons(t[:,:,[0,2]]);ids=np.flatnonzero(shapely.area(p)>1e-10)
    return t[ids],p[ids],ids,shapely.STRtree(p[ids])


def ray_hits(points,t,tree):
    pi,ti=tree.query(shapely.points(points[:,[0,2]]),predicate='covered_by');abc=t[ti];ab=abc[:,1,[0,2]]-abc[:,0,[0,2]];ac=abc[:,2,[0,2]]-abc[:,0,[0,2]];ap=points[pi][:,[0,2]]-abc[:,0,[0,2]];det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det;ys=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1]);top=np.full(len(points),-np.inf);np.maximum.at(top,pi,ys);return top,(pi,ti,ys)


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-west-kowloon-bus-internal-roof-embedding-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name,local=False):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=(HERE/'local'/batch if local else base/batch)/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime='government-xl-next-repairs-west-kowloon-bus-five-original-runtime-v1-20261024';selected={r['uid']:r for r in take(runtime,'selection.json.gz')['rows']};geometry={r['uid']:r for r in take(runtime,'runtime-geometry.json.gz',True)['rows']};attributes=take('government-xl-next-repairs-west-kowloon-bus-five-original-attributes-v1-20261024','attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']};worlds={}
    for uid,row in selected.items():
        p=ROOT/row['candidate']['path'];raw=p.read_bytes();assert digest(raw)==row['sourceSHA256']==attrs[uid]['sourceSHA256']==geometry[uid]['sourceSHA256'];refs.append(p);ix=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3);worlds[uid]={'original':decode_original_world_triangles(raw)}
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(attrs[uid][field],dtype='<f8').reshape(-1,3)[ix]
    pairs=[('landsd/231056:0','landsd/255415:0','government-xl-next-repairs-west-kowloon-bus-roof231056-support-v1-20261024'),('landsd/267223:0','landsd/255415:0','government-xl-next-repairs-west-kowloon-bus-roof267223-support-v1-20261024')];summaries=[]
    for uid,supportuid,proofbatch in pairs:
        prior=take(proofbatch,'summary.json');ground=np.asarray(geometry[uid]['drawnGroundGeometry']).reshape(-1,3,3)
        for mode,t in worlds[uid].items():
            support=worlds[supportuid][mode];old=next(r for r in prior['rows']if r['mode']==mode);assert digest(t.astype('<f8').tobytes())==old['sourceWorldSHA256ByUid'][uid]and digest(support.astype('<f8').tobytes())==old['sourceWorldSHA256ByUid'][supportuid]
            low,high=t.min((0,1)),t.max((0,1));native=ground[(ground[:,:,0].max(1)>=low[0]-1)&(ground[:,:,0].min(1)<=high[0]+1)&(ground[:,:,2].max(1)>=low[2]-1)&(ground[:,:,2].min(1)<=high[2]+1)];g,gp,gids,gt=finite_surface(native);s,sp,sids,st=finite_surface(support);points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1).reshape(-1,3);ground_y,_=ray_hits(points,g,gt);support_y,_=ray_hits(points,s,st);top=np.maximum(ground_y,support_y);gaps=points[:,1]-top;assert np.isfinite(top).all();assert abs(float(gaps.min())-old['compoundFoundation']['minimumGapM'])<1e-9
            bad=np.flatnonzero(gaps<-.5);terrainbad=np.flatnonzero(points[:,1]-ground_y<-.5);assert not len(terrainbad),'Actual ground embedding remains a separate hard failure'
            assert np.all(support_y[bad]>ground_y[bad]),'Every investigated warning must originate in the immutable support source, not terrain'
            _,hits=ray_hits(points[bad],s,st);pi,ti,ys=hits;peak=np.abs(ys-support_y[bad][pi])<1e-9;byface={}
            for k,j in zip(pi[peak],ti[peak]):byface.setdefault(int(bad[k]//4),set()).add(int(sids[j]))
            normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normals,axis=1);ratio=np.divide(normals[:,1],length,out=np.zeros(len(t)),where=length>0);records=[]
            for face,otherfaces in sorted(byface.items()):
                contacts=exact_component_contacts_with_primitives(t,[face],support,sorted(otherfaces),maximum_pairs=1000000);assert contacts['allPairsExamined'];positive=[p for p in contacts['contacts']if p['dimension']>0 and p['primitiveDimensions']==[2,2]];sampleids=[int(k)for k in bad if k//4==face]
                records.append(dict(sourceFace=face,renderable=bool(length[face]>0),normalYRatio=float(ratio[face]),supportPeakFaces=sorted(otherfaces),sampleIndices=sampleids,samples=[dict(point=points[k].tolist(),compoundGapM=float(gaps[k]),trueTerrainGapM=float(points[k,1]-ground_y[k]),supportSourceHeightM=float(support_y[k]),terrainHeightM=float(ground_y[k]))for k in sampleids],exactPeakFaceContacts=contacts,hasFinitePositivePeakFaceContact=bool(positive),sourceSourceIntersectionAccepted=False))
            folder=out/uid.replace('/','-').replace(':','-');save(folder/(mode+'.json.gz'),dict(uid=uid,supportUid=supportuid,mode=mode,sourceWorldSHA256=old['sourceWorldSHA256ByUid'][uid],supportWorldSHA256=old['sourceWorldSHA256ByUid'][supportuid],rows=records));row=dict(uid=uid,supportUid=supportuid,mode=mode,negativeHalfMetreSamples=len(bad),negativeHalfMetreSourceFaces=len(records),actualTerrainNegativeHalfMetreSamples=0,facesWithPositivePeakFaceContact=sum(r['hasFinitePositivePeakFaceContact']for r in records),verticalFaces=sum(r['renderable']and abs(r['normalYRatio'])<=.25 for r in records),otherRenderableFaces=sum(r['renderable']and abs(r['normalYRatio'])>.25 for r in records),nonrenderingFaces=sum(not r['renderable']for r in records),minimumCompoundGapM=float(gaps.min()),minimumActualTerrainGapM=float((points[:,1]-ground_y).min()),sourceSampleHeightRangeM=[float(points[bad,1].min()),float(points[bad,1].max())]if len(bad)else None);summaries.append(row);print(row,flush=True)
    result=dict(uids=list(selected),rows=summaries,allInvestigatedEmbeddingIsSourceAuthored=True,actualTerrainNegativeHalfMetreSamples=0,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact unchanged original/support worlds reproduce each prior compound minimum. Every investigated below-half-metre sample is caused by the original support asset already above that point, not any imported terrain. Complete peak-face finite contact and original face-orientation evidence retained; this is attribution, not permitted internal collision, horizontal-floor, support, architecture or publication acceptance. Generic embedding limits unchanged.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py']);module('west_roof_internal_embedding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fourworld-original-source-internal-versus-terrain-embedding-attribution',refs,result)

if __name__=='__main__':main()
