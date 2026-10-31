"""Bounded primary/source counterpart diagnosis; no identity or physical credit."""
import gzip, importlib.util, json, sys, uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, connect, reservations
sys.path.insert(0, str(HERE.parent/'landsd-territory'))
from source import BASE, request
from exact_original_shell_intersections_20261009 import rational_face, intersection_points

BATCH='government-xl-tuen-mun-special-primary-counterpart-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
RANK=DOC.parent/'government-xl-identity-primary-spatial-ranking-20261009/ranking.json.gz'
SURFACE=DOC.parent/'government-xl-spatial-surface-roles-20261009'
UIDS=['landsd/191896:0','landsd/280350:0']
CSUIDS=['1566329899T20080513','1561229778P20210726']

def module(name, path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def query(table, where, stem, geometry=False):
 params={'f':'json','where':where,'outFields':'*','returnGeometry':'true' if geometry else 'false','outSR':'2326','resultRecordCount':'1000','orderByFields':'OBJECTID'}
 raw,receipt=request(BASE+'/'+str(table)+'/query',params,json_expected=False)
 decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
 data=json.loads(decoded);assert 'features' in data and not data.get('exceededTransferLimit') and not data.get('error')
 (DOC/(stem+'.json')).write_bytes(decoded)
 if raw!=decoded:(DOC/(stem+'.provider-original.gz')).write_bytes(raw)
 save(DOC/(stem+'.request.json'),{**receipt,'decodedSHA256':digest(decoded),'gzipDecoded':raw!=decoded})
 return data

def parity(rings):
 shape=shapely.GeometryCollection()
 for ring in rings:shape=shape.symmetric_difference(shapely.Polygon(ring))
 assert shape.is_valid and shape.area>0
 return shape

def main():
 assert not DOC.exists(),'Fresh immutable diagnostic required'
 claim=reservations.claim('tuen-mun-primary-counterpart-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600)
 assert claim['ok'],claim;lease=claim['reservation'];DOC.mkdir(parents=True)
 paths=[Path(__file__),RANK,HERE.parent/'landsd-territory/source.py',HERE/'exact_original_shell_intersections_20261009.py']
 try:
  primary=query(0,'BuildingCSUID IN ('+','.join("'"+c+"'" for c in CSUIDS)+')','exact-primary',True)
  assert len(primary['features'])==2 and {f['attributes']['BuildingCSUID'] for f in primary['features']}==set(CSUIDS)
  assert primary['spatialReference'].get('latestWkid',primary['spatialReference'].get('wkid'))==2326
  rel=query(1002,'BuildingCSUID IN ('+','.join("'"+c+"'" for c in CSUIDS)+')','exact-structure-relations')
  ids=sorted({f['attributes']['BuildingStructureID'] for f in rel['features']})
  structures=query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-structure-details') if ids else {'features':[]}
  permits=sorted({f['attributes']['OPNo'] for f in structures['features'] if f['attributes'].get('OPNo')})
  if permits:query(1003,'OPNo IN ('+','.join("'"+p.replace("'","''")+"'" for p in permits)+')','same-permit-context')
  records={f['attributes']['BuildingCSUID']:f for f in primary['features']}
  rank=next(r for r in read(RANK)['rows'] if r['uid']==UIDS[0]);sources=[rank,read(SURFACE/'280350-0.json.gz')]
  keys=[r['sourceKey'] for r in sources]
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY')
   models={k+'/'+m['modelId']:m for k,m in c.execute("SELECT cache_key,m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",([k.split('/')[0] for k in keys],[r['modelId'] for r in sources])).fetchall()}
  save(DOC/'native-source-metadata.json.gz',{'models':models,'readOnly':True})
  decoder=module('tuen_mun_original_decode',HERE/'xl-second-pass.py');formsmod=module('tuen_mun_complete_forms',HERE/'xl-final-script-pass.py')
  tris=[];forms=[];bindings=[]
  for r,uid,csuid in zip(sources,UIDS,CSUIDS):
   p=ROOT/r.get('sourcePath',r.get('originalPath'));assert digest(p.read_bytes())==r['sourceSHA256']
   m=models[r['sourceKey']];assert m['asset']['sha256']==r['sourceSHA256'];decoder.LOCAL=p.parent.parent
   tri=decoder.glb_triangles({'sourceSHA256':r['sourceSHA256'],'modelId':r['modelId'],'triangles':m['triangles'],'native':{'model':m}})
   assert len(tri)==m['triangles'] and digest(tri.astype('<f8').tobytes())==r.get('sourceTrianglesSHA256',r.get('worldTrianglesSHA256'))
   lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));near=formsmod.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);own=next(b for b,g,url in near if b['uid']==uid)
   a=records[csuid]['attributes'];assert (a['Status'],a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'])==('Active',own['buildingCSUID'],own['buildingId'],own['structureType'])
   tris.append(tri);forms.append(own);bindings.append({'uid':uid,'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'worldTrianglesSHA256':digest(tri.astype('<f8').tobytes()),'completeOriginalFaces':len(tri),'primaryAttributes':a})
   paths.append(p);paths.extend(ROOT/'3d-viewer'/url for b,g,url in near)
  save(DOC/'complete-original-inputs.json.gz',{'rows':[{**b,'position':t.reshape(-1).tolist()} for b,t in zip(bindings,tris)],'currentForms':forms})
  tower,podium=tris;primary_shapes=[parity([[(x-834500,816500-y) for x,y in ring] for ring in records[c]['geometry']['rings']]) for c in CSUIDS]
  projections=[shapely.union_all(shapely.polygons(t[:,:,[0,2]])) for t in tris]
  extra=projections[0].difference(primary_shapes[0]);foreign=extra.intersection(parity(forms[1]['rings']))
  involved=[]
  for i,t in enumerate(tower):
   p=shapely.Polygon(t[:,[0,2]])
   if p.area and p.intersection(foreign).area>0:involved.append(i)
  # Every face contributing positive-area excess is retained, tested against
  # all original podium faces with intersecting 3D bounds, then exact rationals.
  contacts=[];lo=podium.min(axis=1);hi=podium.max(axis=1);cache={};tests=0
  for i in involved:
   t=tower[i];rat=rational_face(t)
   for j0 in np.flatnonzero(np.all(hi>=t.min(axis=0),axis=1)&np.all(lo<=t.max(axis=0),axis=1)):
    j=int(j0);tests+=1
    if j not in cache:cache[j]=rational_face(podium[j])
    pts=intersection_points(rat,cache[j])
    if pts:contacts.append({'towerFace':i,'podiumFace':j,'positiveDimension':len(pts)>1,'exactPoints':[[str(v) for v in p] for p in sorted(pts)]})
   if len(involved)>50:assert reservations.heartbeat(lease)['ok']
  result={'sourceBindings':bindings,'exactPrimaryRelations':rel['features'],'exactPrimaryStructures':structures['features'],'rawForeignExcessM2':foreign.area,'completeTowerProjectionOutsidePrimaryPodiumM2':projections[0].difference(primary_shapes[1]).area,'primaryTowerFootprintOutsidePrimaryPodiumM2':primary_shapes[0].difference(primary_shapes[1]).area,'towerBaseInsideOfficialPodiumVerticalSpan':bindings[1]['primaryAttributes']['BaseHeight']<=bindings[0]['primaryAttributes']['BaseHeight']<=bindings[1]['primaryAttributes']['TopHeight'],'allExcessContributingOriginalTowerFaces':involved,'allOriginalPodiumAABBPairsTested':tests,'allExactOriginalExcessContacts':contacts,'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'qualification':'Exact original counterpart and fresh official relationship research only. A partial adjacent footprint is not an owned podium by name, proximity or shared OSM. Every source face and raw foreign excess remains. Contact is geometric evidence only; no whole-component support or exception is granted.'}
  save(DOC/'diagnostic.json.gz',result)
  print(json.dumps({'rawForeignExcessM2':foreign.area,'excessFaces':len(involved),'positiveOriginalContacts':sum(c['positiveDimension'] for c in contacts),'officialStructureIds':ids,'permits':permits}),flush=True)
 finally:assert reservations.release(lease)['ok']
 m=module('tuen_mun_diagnostic_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 m.freeze(BATCH,'fresh-primary-and-complete-original-excess-counterpart-v1',paths,{'uids':UIDS,'identityAccepted':False,'physicalAccepted':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'specific-original-excess-ownership-and-complete-current-physical-support-pending','nextStep':'Review exact primary relation and complete original excess contacts; do not apply whole-podium containment contract to an adjacent/partial footprint. Continue independent source identity/support/foundation/runtime checks.'})

if __name__=='__main__':main()
