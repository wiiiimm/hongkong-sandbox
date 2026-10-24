"""New topological failure classification across complete unchanged XL sources.
Not an unchanged acceptance retry: derives missing-area topology and source-face height roles.
All areas/components/neighbours remain present; classifications are diagnostic, not ownership.
"""
import importlib.util,json,uuid,shutil
from collections import Counter
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
from run import ROOT,HERE,read,save,digest,connect,reservations
BATCH='government-xl-spatial-surface-roles-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;OLD=ROOT/'docs/astra-city/government-import'
def mod(n,file):
 s=importlib.util.spec_from_file_location(n,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def polygons(g):
 if g.geom_type=='Polygon':return [g]
 return [p for p in g.geoms if p.geom_type=='Polygon'] if hasattr(g,'geoms') else []
def main():
 rows=[r for r in read(OLD/'government-xl-identity-search-20261009/actionable-dispositions.json.gz')['rows'] if r['identityState']=='complete-original-component-coverage-unresolved'];assert len(rows)==179
 groups={r['uid']:r for r in read(OLD/'government-xl-322-complete-footprint-group-scan-v2-20261008/outcomes.json.gz')['rows']};op={r['uid']:r for r in read(OLD/'government-xl-identity-search-op-structures-20261009/full-original-op-group-measures.json.gz')['rows']};decoder=mod('surface_roles_exact_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;final=mod('surface_roles_current_forms','xl-final-script-pass.py');out=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');native={k+'/'+m['modelId']:m for k,m in c.execute("SELECT cache_key,m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",(list({r['sourceKey'].split('/')[0] for r in rows}),[r['modelId'] for r in rows])).fetchall()}
 # Put new primary-evidence leads first, then the twelve explicit OP relationship variants.
 rows.sort(key=lambda r:(r['uid'] not in ['landsd/173512:0','landsd/263423:0'],r['uid'] not in op,r['uid']))
 for r in rows:
  uid=r['uid'];path=DOC/(uid.split('/')[1].replace(':','-')+'.json.gz')
  if path.exists():out.append(read(path));continue
  claim=reservations.claim('xl-surface-role-'+str(uuid.uuid4()),['native-model:'+r['sourceKey']],batch=BATCH,ttl=1800)
  if not claim['ok']:
   print(json.dumps({'uid':uid,'reservedElsewhere':True}),flush=True);continue
  lease=claim['reservation']
  try:
   g=groups[uid]
   if not g.get('original') or not g.get('groupForms'):
    item={k:r[k] for k in ['uid','name','modelId','sourceKey','sourceSHA256']};item.update(variants={},diagnosticFamilies=['prior-complete-group-proof-unavailable'],priorReasons=g['reasons'],nextStep='Recover exact original/group proof before complete surface-role analysis; no inference from failed prior group job.',identityAccepted=False,installationApproved=False,geometryChanges=0);save(path,item);out.append(item);continue
   source=ROOT/g['original']['path'];sha=r['sourceSHA256'];assert digest(source.read_bytes())==sha==g['sourceSHA256'];m=native[r['sourceKey']];asset=LOCAL/'assets'/(sha+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,asset);tri=decoder.glb_triangles({'sourceSHA256':sha,'modelId':r['modelId'],'triangles':m['triangles'],'native':{'model':m}});assert not g.get('worldTrianglesSHA256') or digest(tri.astype('<f8').tobytes())==g['worldTrianglesSHA256'];projection=final.projection(tri);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);target=next(b for b,p,t in forms if b['uid']==uid);tilepins={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for b,p,t in forms};variants={};groupvariants={'direct-shared-OSM':g['groupForms']}
   if uid in op:groupvariants['official-OP-structure']=op[uid]['groupForms']
   for key,group in groupvariants.items():
    for b in group:
     match=next((x for x,_,_ in forms if x['uid']==b['uid']),None)
     if match is not None:assert match==b
    foot=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:]) for b in group]);missing=foot.difference(projection);excess=projection.difference(foot);parts=polygons(missing);boundary=[p for p in parts if p.distance(foot.boundary)<=1e-8];interior=[p for p in parts if p.distance(foot.boundary)>1e-8];uids={b['uid'] for b in group};overlaps=[]
    for b,p,t in forms:
     if b['uid'] in uids:continue
     ov=excess.intersection(p)
     if ov.area<=1e-8:continue
     facep=shapely.polygons(tri[:,:,[0,2]]);hit=(shapely.area(facep)>1e-10)&shapely.intersects(facep,ov);faces=tri[hit];overlaps.append({'uid':b['uid'],'name':b.get('name'),'areaM2':float(ov.area),'buildingBase':b.get('base'),'buildingTop':(b.get('base') or 0)+(b.get('height') or 0),'sourceFaceCount':len(faces),'sourceYRange':[float(faces[:,:,1].min()),float(faces[:,:,1].max())] if len(faces) else None,'geometry':mapping(ov)})
    distances=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3);far=distances.max(axis=1)>10;farfaces=tri[far];stats={'targetAreaM2':float(foot.area),'sourceProjectionAreaM2':float(projection.area),'missingTotalAreaM2':float(missing.area),'missingBoundaryConnectedAreaM2':float(sum(p.area for p in boundary)),'missingInteriorAreaM2':float(sum(p.area for p in interior)),'missingInteriorComponentCount':len(interior),'missingBoundaryComponentCount':len(boundary),'sourceExcessAreaM2':float(excess.area),'excessOverOtherFormsM2':float(sum(x['areaM2'] for x in overlaps)),'targetCoverage':float(foot.intersection(projection).area/foot.area),'maximumSourceExtentM':float(distances.max()),'sourceFacesBeyond10m':len(farfaces),'farSourceYRange':[float(farfaces[:,:,1].min()),float(farfaces[:,:,1].max())] if len(farfaces) else None,'farSourceBounds':[farfaces.min(axis=(0,1)).tolist(),farfaces.max(axis=(0,1)).tolist()] if len(farfaces) else None}
    families=[]
    if stats['targetCoverage']<.95:families.append('missing-interior-area' if stats['missingInteriorAreaM2']>.5*stats['missingTotalAreaM2'] else 'missing-outer-boundary-or-components')
    if stats['maximumSourceExtentM']>10:families.append('source-authored-extra-extent-role-unresolved')
    if stats['excessOverOtherFormsM2']>1:families.append('overlapping-source-surface-ownership-unresolved')
    if not families:families.append('bounds-pass-other-identity-contract-unresolved')
    variants[key]={'stats':stats,'diagnosticFamilies':families,'groupForms':group,'overlappingForms':overlaps,'largestMissingComponents':[{'areaM2':float(p.area),'interior':p.distance(foot.boundary)>1e-8,'geometry':mapping(p)} for p in sorted(parts,key=lambda p:-p.area)[:12]],'sourceProjectionInteriorHolesM2':sum(Polygon(ring).area for p in polygons(projection) for ring in p.interiors)}
    if uid in ['landsd/173512:0','landsd/263423:0'] or uid in op:
     save(DOC/uid.split('/')[1].replace(':','-')/(key+'-exact-surface-roles.geojson'),{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'role':name},'geometry':mapping(geom)} for name,geom in [('all-original-projection',projection),('all-group-target',foot),('uncovered-target',missing),('all-source-excess',excess)]]});np.savez_compressed(LOCAL/'surface-faces'/ (uid.split('/')[1].replace(':','-')+'-'+key+'.npz'),farFaceIndices=np.flatnonzero(far),farTriangles=farfaces)
   item={k:r[k] for k in ['uid','name','modelId','sourceKey','sourceSHA256']};item.update(originalPath=str(source.relative_to(ROOT)),worldTrianglesSHA256=digest(tri.astype('<f8').tobytes()),variants=variants,sourceTileHashes=tilepins,identityAccepted=False,installationApproved=False,geometryChanges=0,qualification='New missing-area topology and original-face height roles only, not courtyard/canopy/bridge semantic proof. Every source face and target/group/neighbour retained; no unchanged acceptance retry or threshold waiver.');save(path,item);out.append(item);print(json.dumps({'uid':uid,'name':r['name'],'checked':len(out),'families':{k:v['diagnosticFamilies'] for k,v in variants.items()}}),flush=True)
  finally:assert reservations.release(lease)['ok']
  save(DOC/'progress.json',{'checked':len(out),'total':179})
 save(DOC/'topological-failure-ranking.json.gz',{'rows':out,'totalRequested':179,'checked':len(out),'diagnosticOnly':True,'semanticRolesNeedPrimaryEvidence':True})
if __name__=='__main__':
 (LOCAL/'surface-faces').mkdir(parents=True,exist_ok=True);main()
