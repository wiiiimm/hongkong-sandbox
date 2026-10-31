"""Bound complete original geometry and enumerate every foreign excess actor.

This diagnostic cannot grant identity, physical or installation credit. Shared
occupation records and source form parents are reported, never used as waivers.
"""
import importlib.util,json,uuid
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from popcorn_primary_original_identity_v2_20261009 import UIDS,verify_files,DOC as PRIMARY

BATCH='government-xl-popcorn-primary-excess-ownership-v2-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-current-overlapping-original-recovery-20261009/selection.json.gz'

def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists(),'Fresh immutable diagnostic required'
 rows=[r for r in read(INPUT)['rows'] if r['uid'] in UIDS];assert {r['uid'] for r in rows}==UIDS
 claim=reservations.claim('popcorn-complete-excess-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 decoder=module('complete_excess_original_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL;(LOCAL/'assets').mkdir(parents=True)
 forms_module=module('complete_excess_current_forms','xl-final-script-pass.py');summaries=[];paths=[Path(__file__),HERE/'popcorn_primary_original_identity_v2_20261009.py',HERE/'test_popcorn_primary_original_identity_v2_20261009.py',INPUT,PRIMARY/'result.json']
 try:
  for row in rows:
   assert reservations.heartbeat(lease)['ok'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw);row['triangles']=row['native']['model']['triangles']
   tri=decoder.glb_triangles(row);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=forms_module.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);stem=row['uid'].split('/')[1].replace(':','-')
   context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':forms_module.identity_context(row,tri,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}}
   save(DOC/(stem+'-context.json.gz'),context);proof=verify_files(row,context,LOCAL/'identity'/stem);save(DOC/(stem+'-identity.json'),proof)
   provider=read(PRIMARY/(stem+'-provider.json'));g=provider['features'][0]['geometry'];rings=[[(v[0]-834500,816500-v[1]) for v in ring] for ring in g['rings']];target=shapely.Polygon(rings[0],rings[1:]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));excess=projection.difference(target)
   foreign=[]
   for building,_,url in forms:
    if building['uid']==row['uid']:continue
    shape=shapely.Polygon(building['rings'][0],building['rings'][1:]);area=excess.intersection(shape).area
    if area>1e-8:foreign.append({'uid':building['uid'],'name':building.get('name'),'buildingCSUID':building.get('buildingCSUID'),'structureType':building.get('structureType'),'overlapM2':area,'wholeSourceTargetCoverage':projection.intersection(shape).area/shape.area,'currentForm':building,'tile':ref(ROOT/'3d-viewer'/url)})
   relations=read(PRIMARY/(stem+'-op-relations.json'));item={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'originalFaces':len(tri),'worldTrianglesSHA256':proof['worldTrianglesSHA256'],'identityPassed':proof['passed'],'reasons':proof['reasons'],'completePrimaryExcessM2':excess.area,'foreignActors':sorted(foreign,key=lambda x:-x['overlapM2']),'rawOccupationRelations':relations['features'],'occupationRelationsUsedForSpatialCredit':False,'sharedParentUsedForForeignExemption':False,'nextStep':'Verify exact excess actor primary lineage and original geometry/support interfaces; keep complete physical/runtime checks. No group exemption.'}
   save(DOC/(stem+'-foreign-actors.json'),item);summaries.append(item);paths +=[ROOT/row['candidate']['path']]+[ROOT/'3d-viewer'/url for _,_,url in forms]
   print(json.dumps({'uid':row['uid'],'identityPassed':proof['passed'],'foreignActors':[{k:x[k] for k in ['uid','name','structureType','overlapM2']} for x in item['foreignActors']]}),flush=True)
  save(DOC/'summary.json',{'rows':summaries,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0})
 finally:assert reservations.release(lease)['ok']
 module('complete_excess_neon_checkpoint','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-complete-original-primary-excess-ownership-v2',paths,{'uids':sorted(UIDS),'identityAccepted':False,'physicalAccepted':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'exact-source-excess-actor-ownership-and-complete-physical-support-pending','nextStep':'Use each recorded foreign actor to recover exact authoritative podium/ancillary lineage and unchanged original interfaces; all failed checks retained.'})
if __name__=='__main__':main()
