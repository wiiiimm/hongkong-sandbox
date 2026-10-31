"""Fresh authoritative lineage and complete projected geometry diagnostics only.

No identity/physical acceptance, geometry edits, footprint replacement or skip
credit. Every prior failed identity reason remains attached to the source.
"""
import importlib.util,json,sys,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
from government_georef_cell_identity import geographic_cell
BATCH='government-xl-popcorn-six-held-primary-lineage-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-overlapping-original-current-identity-20261009'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-current-overlapping-original-recovery-20261009/selection.json.gz'
IDS={186723,295536,295421,295425,309558,53924}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fetch(name,layer,where,geometry):
 params={'f':'json','where':where,'outFields':'*','returnGeometry':str(geometry).lower(),'resultRecordCount':'1000'}
 if geometry:params['outSR']='2326'
 raw,receipt=request(BASE+'/'+str(layer)+'/query',params);path=DOC/(name+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);save(DOC/(name+'.request.json'),receipt)
 data=json.loads(raw);assert not data.get('error') and not data.get('exceededTransferLimit')
 return data

def main():
 assert not DOC.exists() and not LOCAL.exists(),'Fresh immutable diagnostic stage required'
 rows=[r for r in read(INPUT)['rows'] if r['source']['building']['objectId'] in IDS];assert len(rows)==6
 claim=reservations.claim('popcorn-primary-lineage-'+str(uuid.uuid4()),['building:'+r['uid'] for r in rows],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 decoder=module('popcorn_primary_original_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL;(LOCAL/'assets').mkdir(parents=True)
 final=module('popcorn_primary_current_forms','xl-final-script-pass.py');summaries=[];paths=[Path(__file__),INPUT,HERE/'government_georef_cell_identity.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']
 try:
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(DOC/'starting-manifest.json').parent.mkdir(parents=True);(DOC/'starting-manifest.json').write_bytes(before)
  for r in rows:
   assert reservations.heartbeat(lease)['ok'];form=r['source']['building'];uid=r['uid'];stem=uid.split('/')[1].replace(':','-');csuid=form['buildingCSUID']
   raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];(LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz')).write_bytes(raw);r['triangles']=r['native']['model']['triangles'];tri=decoder.glb_triangles(r);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));cell=geographic_cell(r['modelId'],csuid,form['structureType'])
   lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);assert [b for b,_,_ in forms if b['uid']==uid]==[form]
   context=final.identity_context(r,tri,forms);save(DOC/(stem+'-current-context.json.gz'),context);paths.extend(ROOT/'3d-viewer'/u for _,_,u in forms)
   provider=fetch(stem+'-provider',0,"BuildingCSUID='"+csuid+"'",True);relations=fetch(stem+'-op-relations',1002,"BuildingCSUID='"+csuid+"'",False)
   structure_ids=sorted({f['attributes']['BuildingStructureID'] for f in relations['features']});structures=fetch(stem+'-op-structures',1003,'BuildingStructureID IN('+','.join(map(str,structure_ids))+')',False) if structure_ids else {'features':[]}
   official=[]
   for f in provider['features']:
    a=f['attributes'];assert a['BuildingCSUID']==csuid;g=f.get('geometry');shape=None
    if g:
     sr=g.get('spatialReference',provider.get('spatialReference',{}));assert sr.get('latestWkid',sr.get('wkid'))==2326
     rings=[[(v[0]-834500,816500-v[1]) for v in ring] for ring in g['rings']];shape=shapely.Polygon(rings[0],rings[1:]);assert shape.is_valid and shape.area>0
    item={'attributes':a,'geometryAvailable':shape is not None}
    if shape is not None:item.update(completeOfficialTargetAreaM2=shape.area,officialTargetCoveredByWholeOriginalProjection=projection.intersection(shape).area/shape.area,originalProjectionExcessBeyondOfficialTargetM2=projection.difference(shape).area,officialGeoRefCellCoveredFraction=shape.intersection(cell).area/cell.area,currentVersusOfficialSymmetricDifferenceM2=shape.symmetric_difference(shapely.Polygon(form['rings'][0],form['rings'][1:])).area)
    official.append(item)
   prior=read(PRIOR/(stem+'-identity.json'));assert not prior['passed'] and prior['reasons']
   summary={'uid':uid,'name':form.get('name'),'sourceSHA256':r['sourceSHA256'],'modelId':r['modelId'],'completeOriginalFaces':len(tri),'originalWorldTrianglesSHA256':digest(tri.astype('<f8').tobytes()),'priorIdentityReasonsRetained':prior['reasons'],'freshCurrentSpatialContext':context,'freshAuthoritativeRecords':official,'occupationStructureIds':structure_ids,'occupationStructures':[f['attributes'] for f in structures['features']],'originalGeoRefCellCoveredFraction':projection.intersection(cell).area/cell.area,'sourceGeometryChanges':0,'identityAccepted':False,'installationApproved':False,'requiresMoreComputeOrSourceEvidence':True}
   save(DOC/(stem+'-diagnostic.json'),summary);summaries.append(summary);paths += [ROOT/r['candidate']['path'],PRIOR/(stem+'-identity.json')];print(json.dumps({k:summary[k] for k in ['uid','name','priorIdentityReasonsRetained','freshAuthoritativeRecords','originalGeoRefCellCoveredFraction']}),flush=True)
  assert reservations.owns(lease);save(DOC/'diagnostic.json.gz',{'rows':summaries,'startingManifestSHA256':digest(before),'endingManifestSHA256':digest(manifest.read_bytes()),'publication':False,'sourceGeometryChanges':0,'identityAccepted':False,'qualification':'Fresh primary records and complete original projected geometry only. All failed identity reasons retained. Changed unrelated global manifest is recorded; each regional source tile remains independently pinned. No installation or permanent rejection.'})
  module('popcorn_primary_lineage_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-held-originals-fresh-primary-lineage-diagnostic-v1',paths,{'uids':sorted(r['uid'] for r in rows),'identityAccepted':False,'physicalAccepted':False,'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'source-specific-complete-identity-recovery-pending','nextStep':'Use fresh official shapes and occupation-structure provenance to investigate the six existing failures; retain all physical/runtime/foreign/browser gates. Diagnostic record grants no acceptance or install credit.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
