"""Exact complete Tower8-to-original-podium geometry and primary relationship.

Permit context alone gives no assembly ownership, identity, or support credit.
"""
import collections,json,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-yoho-eight-original-podium-contacts-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-yoho-eight-primary-podium-discovery-20261009/original-source-lookup.json.gz'
ASSETS=[HERE/'local/government-xl-spatial-surface-roles-20261009/assets/fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08.glb.gz',HERE/'local/government-xl-five-more-original-supports-current-inputs-20261007/assets/d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167.glb.gz']
UIDS=['landsd/146396:0','landsd/231756:0']
def poly(feature):
 out=Polygon()
 for ring in feature['geometry']['rings']:out=out.symmetric_difference(Polygon([(x-834500,-y+816500) for x,y in ring]))
 return out
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();claim=reservations.claim('yoho-eight-originals-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  d=read(INPUT);ts=[]
  for row,path in zip(d['rows'],ASSETS):
   assert digest(path.read_bytes())==row['model']['asset']['sha256'];ts.append(decode_original_world_triangles(path.read_bytes()))
  tower,podium=ts;tc=components(tower);pc=components(podium);ids=list(range(len(podium)));rows=[]
  for c in tc['components']:
   f=[i for i in c['faceIndices'] if np.linalg.norm(np.cross(tower[i,1]-tower[i,0],tower[i,2]-tower[i,0]))>0]
   if not f:rows.append({'originalTowerFaces':c['faceIndices'],'collapsedOnly':True,'supportCredit':False});continue
   contacts=exact_component_contacts(tower,f,podium,ids,maximum_pairs=1000000)
   rows.append({'originalTowerFaces':c['faceIndices'],'originalComponent':{k:v for k,v in c.items() if k!='faceIndices'},'exactCompleteOriginalPodiumInterfaces':contacts,'positiveContactCount':sum(x['dimension']>0 for x in contacts['contacts']),'supportCredit':False})
  primary={r['attributes']['BuildingCSUID']:r for r in d['primaryRecords']};a=primary['2179133649T20050430'];b=primary['2187833636P20050609'];pa,pb=poly(a),poly(b)
  result={'uids':UIDS,'sourceSHA256s':[r['model']['asset']['sha256'] for r in d['rows']],'completeWorldSHA256s':[digest(t.astype('<f8').tobytes()) for t in ts],'completeOriginalFaceCounts':[len(t) for t in ts],'completeOriginalComponentCounts':[len(tc['components']),len(pc['components'])],'completeTowerComponents':rows,'primaryTowerAreaM2':pa.area,'primaryTowerInsidePodiumAreaM2':pa.intersection(pb).area,'primaryTowerOutsidePodiumAreaM2':pa.difference(pb).area,'primaryTowerWithinPodiumVerticalSpan':b['attributes']['BaseHeight']<=a['attributes']['BaseHeight']<=b['attributes']['TopHeight'],'exactPrimaryRelations':d['exactRelations'],'exactPrimaryStructures':d['exactStructures'],'primaryDistinctStructureIDsRetained':True,'samePermitOnlyContextual':True,'evidenceRefs':[ref(p) for p in [Path(__file__),INPUT,*ASSETS,HERE/'exact_packed_world_geometry_20261009.py',HERE/'source_closed_components.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']],'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'publication':False,'qualification':'Every original Tower8 component compared to every original podium triangle via inclusive unpadded bounds and exact rational intersections. Same occupation permit is contextual only; distinct structure identifiers remain. Positive original interfaces do not certify support through an absent original podium or remove actual current podium/other foreign gates.'}
  save(DOC/'diagnostic.json.gz',result);summary={'completeOriginalFaces':[len(t) for t in ts],'towerComponents':len(rows),'componentsWithPositiveContact':sum(bool(r.get('positiveContactCount')) for r in rows),'componentsWithoutPositiveContact':[len(r['originalTowerFaces']) for r in rows if not r.get('positiveContactCount')],'primaryTowerOutsidePodiumAreaM2':result['primaryTowerOutsidePodiumAreaM2'],'verticalSpan':result['primaryTowerWithinPodiumVerticalSpan'],'physicalAccepted':False};save(DOC/'summary.json',summary);print(json.dumps(summary),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
