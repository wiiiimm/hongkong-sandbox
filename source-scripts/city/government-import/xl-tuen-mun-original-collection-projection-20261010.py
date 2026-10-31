"""Measure every recovered original hospital actor; no assembly acceptance.

Separate source towers can occupy primary podium holes. This diagnostic
records the actual remaining gaps without filling holes or grouping actors.
"""
import gzip,importlib.util,json,sys,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_ownership import document,graph_reasons
from tuen_mun_named_original_hospital_identity_20261010 import polygon,SPEC,RELATED
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
BATCH='government-xl-tuen-mun-original-collection-projection-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
SOURCE=DOC.parent/'government-xl-tuen-mun-main-block-source-collection-20261010'
COUNTERPART=DOC.parent/'government-xl-tuen-mun-special-primary-counterpart-20261009'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not (DOC/'result.json').exists()
 collection=read(SOURCE/'selection.json.gz');receipt=read(SOURCE/'result.json')
 refs=receipt['evidenceRefs']
 for r in refs:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 rows=collection['rows'];uids=[r['uid'] for r in rows]+[RELATED]
 claim=reservations.claim('hospital-collection-projection-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  DOC.mkdir(parents=True,exist_ok=True)
  entries={a['modelId']:a for a in collection['completeOriginalAcquisition']['assets']}
  originals=[];paths=[]
  for r in rows:
   a=entries[r['modelId']];p=ROOT/a['path'];raw=p.read_bytes();m=r['native']['model']
   assert digest(raw)==r['sourceSHA256']==m['asset']['sha256'] and not graph_reasons(document(raw),r['modelId'],m['triangles'])
   originals.append((r['uid'],p,decode_original_world_triangles(raw),m));paths.append(p)
  prior=read(COUNTERPART/'result.json');p=next(ROOT/r['path'] for r in prior['evidenceRefs'] if r['sha256']==SPEC[RELATED][2] and '/assets/' in r['path'])
  raw=p.read_bytes();assert digest(raw)==SPEC[RELATED][2] and not graph_reasons(document(raw),SPEC[RELATED][0],SPEC[RELATED][1])
  tri=decode_original_world_triangles(raw);assert digest(tri.astype('<f8').tobytes())==SPEC[RELATED][3]
  metadata=read(COUNTERPART/'native-source-metadata.json.gz')['models'];m=next(m for m in metadata.values() if m['modelId']==SPEC[RELATED][0]);originals.append((RELATED,p,tri,m));paths.append(p)
  final=module('hospital_collection_current_forms','xl-final-script-pass.py')
  alltri=np.concatenate([t for _,_,t,_ in originals]);lo,hi=alltri.min(axis=(0,1)),alltri.max(axis=(0,1));loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[f for f,_,_ in loaded];hashes={u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in loaded}
  csuids=[next(f for f in forms if f['uid']==uid)['buildingCSUID'] for uid,_,_,_ in originals]
  where='BuildingCSUID IN ('+','.join("'"+c+"'" for c in csuids)+')'
  params=dict(f='json',where=where,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
  raw,rec=request(BASE+'/0/query',params,json_expected=False);decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
  primary=json.loads(decoded);assert not primary.get('error') and not primary.get('exceededTransferLimit') and len(primary['features'])==len(originals)
  assert primary['spatialReference'].get('latestWkid',primary['spatialReference'].get('wkid'))==2326
  (DOC/'exact-primary.json').write_bytes(decoded)
  if raw!=decoded:(DOC/'exact-primary.provider-original.gz').write_bytes(raw)
  save(DOC/'exact-primary.request.json',{**rec,'decodedSHA256':digest(decoded),'gzipDecoded':raw!=decoded})
  bycs={f['attributes']['BuildingCSUID']:f for f in primary['features']};assert set(bycs)==set(csuids)
  manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());measurements=[];projections={}
  for uid,path,t,m in originals:
   current=next(f for f in forms if f['uid']==uid);provider=bycs[current['buildingCSUID']];a=provider['attributes']
   assert (a['Status'],a['BuildingID'],a['BuildingBlockType'])==('Active',current['buildingId'],current['structureType'])
   q=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));projections[uid]=q
   metrics=[]
   for name,p in [('current',polygon(current['rings'])),('primary',polygon(provider['geometry']['rings'],True))]:
    metrics.append(dict(basis=name,coverage=q.intersection(p).area/p.area,maximumExtentM=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),p).max()),sourceProjectionOutsideOwnM2=q.difference(p).area))
   measurements.append(dict(uid=uid,modelId=m['modelId'],sourceSHA256=digest(path.read_bytes()),worldTrianglesSHA256=digest(t.astype('<f8').tobytes()),completeOriginalFaces=len(t),sourcePath=str(path.relative_to(ROOT)),nativeState=m.get('state'),currentForm=current,primaryRecord=provider,wholeOwnSpatial=metrics))
  podium=next(r for r in measurements if r['uid']==RELATED);primaryshape=polygon(podium['primaryRecord']['geometry']['rings'],True);gap=primaryshape.difference(projections[RELATED]);collectionprojection=shapely.union_all(list(projections.values()));residual=primaryshape.difference(collectionprojection)
  pieces=list(residual.geoms) if hasattr(residual,'geoms') else [residual]
  result=dict(measurements=measurements,completeOriginalFaces=sum(r['completeOriginalFaces'] for r in measurements),rawPodiumMissingProjectionM2=gap.area,rawPodiumMissingProjectionBounds=list(gap.bounds),separateOriginalTowersInPodiumGaps=[dict(uid=uid,actualOriginalCoverageOfPodiumGapM2=q.intersection(gap).area) for uid,q in projections.items() if uid!=RELATED],completeOriginalCollectionPodiumPrimaryCoverage=collectionprojection.intersection(primaryshape).area/primaryshape.area,remainingUncoveredPrimaryPodiumProjectionM2=residual.area,remainingGapComponents=[dict(areaM2=p.area,bounds=list(p.bounds)) for p in sorted(pieces,key=lambda p:-p.area) if p.area>0],primaryPodiumRingsUnchanged=True,sourceGeometryChanges=0,commonSiteGroupingApproved=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,manifestSHA256=msha,neighbourTileHashes=hashes)
  save(DOC/'diagnostic.json.gz',result);save(DOC/'complete-current-forms.json.gz',dict(forms=forms,tileHashes=hashes));assert digest(manifest.read_bytes())==msha
  fence=module('hospital_collection_projection_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');fence.freeze(BATCH,'complete-original-hospital-collection-individual-projection-diagnostic-v1',[Path(__file__),SOURCE/'result.json',SOURCE/'selection.json.gz',COUNTERPART/'native-source-metadata.json.gz',manifest,*paths,*[ROOT/'3d-viewer'/u for u in hashes]],dict(uids=uids,identityAccepted=False,physicalAccepted=False,requiresAIModelGeometry=False,requiresHumanDecision=False,remainingReason='complete-individual-primary-current-source-roles-and-physical-checks-pending',nextStep='Use measured separate source coverage to identify genuine actor partitions; retain every raw own coverage/extent, current neighbour, source hole and physical gate. No assembly grouping waiver.'))
  print(json.dumps({k:result[k] for k in ['completeOriginalFaces','rawPodiumMissingProjectionM2','completeOriginalCollectionPodiumPrimaryCoverage','remainingUncoveredPrimaryPodiumProjectionM2','sourceGeometryChanges','installationApproved']}),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
