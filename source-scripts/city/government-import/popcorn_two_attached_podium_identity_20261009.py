"""Two named original roof parts attached to an independently identified podium.

Identity only: all current actors and all physical/support checks remain required.
"""
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import numpy as np
import shapely
from run import ROOT,HERE,read,digest,connect
from popcorn_primary_original_identity_v2_20261009 import verify_files as prior_verify
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts

PODIUM='landsd/295538:0'
PARENT=('4479918772P20110808',1810071458,'Podium')
PARENT_SOURCE='9dc37f891dc96d8ce8be29da04138e347e7bea4924f7e709e793ad3495ac539f'
PARENT_WORLD='70cd147ff3c2a8eca67bf96993695af399ff974022e3d4580990bca816e6262f'
PARTS={
 'landsd/295421:0':('4487218868T20110805',1810071419,22,'790e9faab9ab82676d294d4f5e647204b7b79356cff6db9cbf60b64c3558922a','16e51e877d58e91af6bdb6c6058f6d1be29eeb73ca83c2aaf7e8e74667123214',7),
 'landsd/295425:0':('4476718730T20110808',1810071432,26,'1d04c76fed9c17340b9d88f3e703561b78c4f0b91c11ded15501f3223e8b039d','c138ceeb8b78c300633a459c1a1f488200c54d498f781168443386d5535b555c',31),
}
POLICY='two-named-source-attached-primary-podium-identity-v1'
REASON='fresh-primary-full-source-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2'
BASE=ROOT/'docs/astra-city/government-import'
RELATION=BASE/'government-xl-popcorn-two-original-primary-podium-relation-20261009'
PRIMARY=BASE/'government-xl-popcorn-six-held-primary-lineage-20261009'
PARENT_INPUT=BASE/'government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
JOB='6062cce0cda21b8bc22454787ce56c8a2b88a39c7c7ea1c6662d12793f5623ee'

def polygon(rings):
 result=shapely.GeometryCollection()
 for ring in rings: result=result.symmetric_difference(shapely.Polygon(ring))
 assert result.is_valid and result.area>0
 return result

def primary(provider,form,expected):
 assert not provider.get('error') and not provider.get('exceededTransferLimit') and len(provider['features'])==1
 sr=provider['spatialReference'];assert sr.get('latestWkid',sr.get('wkid'))==2326
 feature=provider['features'][0];a=feature['attributes'];csuid,bid,kind=expected
 assert (form['buildingCSUID'],form['buildingId'],form['structureType'])==expected
 assert (a['Status'],a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'],a['GeoRefNo'])==('Active',csuid,bid,kind,csuid[:10])
 assert isinstance(a.get('DateCreate'),(int,float)) and datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:]
 assert np.isfinite([a['BaseHeight'],a['TopHeight']]).all() and a['BaseHeight']<a['TopHeight']
 return a,polygon([[(x-834500,816500-y) for x,y in ring] for ring in feature['geometry']['rings']])

def named_proof(previous,row,triangles,forms,providers,parent_input):
 assert row['uid'] in PARTS
 csuid,bid,count,source_sha,world_sha,expected_contacts=PARTS[row['uid']]
 assert row['sourceSHA256']==source_sha and row['modelId']=='B'+csuid[:10]+'01063C0' and row['triangles']==count
 assert previous['uid']==row['uid'] and previous['sourceSHA256']==source_sha and previous['originalOwnership']['sourceGraphVerified'] and previous['worldTrianglesSHA256']==world_sha
 assert REASON in previous['reasons'],'Specific retained primary podium overlap required'
 tri=np.asarray(triangles,dtype='<f8');assert tri.shape==(count,3,3) and np.isfinite(tri).all() and digest(tri.tobytes())==world_sha
 by_uid={b['uid']:b for b in forms};assert len(by_uid)==len(forms) and PODIUM in by_uid and by_uid[row['uid']]==row['source']['building']
 own=by_uid[row['uid']];parent=by_uid[PODIUM]
 own_a,own_shape=primary(providers[row['uid']],own,(csuid,bid,'Tower'))
 parent_a,parent_shape=primary(providers[PODIUM],parent,PARENT)
 current_own=polygon(own['rings']);current_parent=polygon(parent['rings'])
 assert own_shape.difference(parent_shape).area==0 and current_own.difference(current_parent).area==0
 assert parent_a['BaseHeight']<=own_a['BaseHeight']<=parent_a['TopHeight']
 assert np.isfinite([parent['base'],parent['height'],own['base']]).all() and parent['height']>0
 assert parent['base']<=own['base']<=parent['base']+parent['height']
 assert parent_input['uid']==PODIUM and parent_input['sourceSHA256']==PARENT_SOURCE and parent_input['worldTriangleSHA256']==PARENT_WORLD and parent_input['triangles']==15367
 body=np.asarray(parent_input['position'],dtype='<f8').reshape(-1,3,3)
 assert body.shape==(15367,3,3) and np.isfinite(body).all() and digest(body.tobytes())==PARENT_WORLD
 body_faces=np.flatnonzero(np.any(np.cross(body[:,1]-body[:,0],body[:,2]-body[:,0])!=0,axis=1))
 source_components=components(tri)['components'];accounted=[];contacts=[]
 for component in source_components:
  indices=component['faceIndices'];accounted+=indices
  positive=[i for i in indices if np.any(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0])!=0)]
  contact=exact_component_contacts(tri,positive,body,body_faces,first_only=False) if positive else {'contacts':[]}
  assert any(c['dimension']>0 for c in contact['contacts']),'Every original component must attach to the exact original podium'
  contacts.append(contact)
 assert sorted(accounted)==list(range(count)) and len(set(accounted))==len(accounted)
 assert sum(c['dimension']>0 for p in contacts for c in p['contacts'])==expected_contacts
 projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
 assert projection.difference(parent_shape).area==0 and projection.difference(current_parent).area==0
 foreign=[b for b in forms if b['uid'] not in {row['uid'],PODIUM}]
 foreign_shape=shapely.union_all([polygon(b['rings']) for b in foreign]);checks={};reasons=[r for r in previous['reasons'] if r!=REASON]
 for name,target in [('primary',own_shape),('current',current_own)]:
  extra=projection.difference(target)
  m={'coverage':projection.intersection(target).area/target.area,'maximumExtentM':float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max()),'unrelatedExcessM2':extra.intersection(foreign_shape).area,'rawRelatedPodiumExcessM2':extra.intersection(current_parent).area}
  checks[name]=m
  if not(.95<=m['coverage']<=1.000000001 and m['maximumExtentM']<=10 and m['unrelatedExcessM2']<=1):reasons.append('complete-named-part-'+name+'-spatial-bound')
 passed=not reasons;out=deepcopy(previous)
 out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawPodiumForeignReasonsRetained=[REASON],explicitRelatedPodiumUID=PODIUM,primaryPartAttributes=own_a,primaryPodiumAttributes=parent_a,completeExactOriginalContactChecks=contacts,independentFullSourceSpatialChecks=checks,allOtherActorsStillForeignUIDs=sorted(b['uid'] for b in foreign),currentPodiumForm=parent,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,podiumRemoval=False,podiumCollisionExemption=False,podiumGroundSupportCredit=False,qualification='Only two named unchanged original sources with unique stable primary Tower identities and full own footprints inside an explicitly identified active primary/current Podium; recorded bases are inside its vertical span. Every complete original component independently has exact positive-dimensional contacts to the pinned15367-face original podium. Both own footprints meet95%/10m/1m² bounds; only that exact podium is related for identity. Every raw overlap remains and every other actor stays foreign. No name/OSM/OP grouping, collision/support/terrain/runtime exemption or installation credit.')
 return out

def verify_files(row,context,local):
 previous=prior_verify(row,context,local);receipt=read(RELATION/'result.json');assert receipt['jobId']==JOB
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 def module(name,file):
  spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 decoder=module('named_podium_original_decoder','xl-second-pass.py');decoder.LOCAL=local;tri=decoder.glb_triangles(row)
 final=module('named_podium_complete_current_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 for _,_,url in forms:assert digest((ROOT/'3d-viewer'/url).read_bytes())==context['neighbourTileHashes'][url]
 providers={};stem=row['uid'].split('/')[1].replace(':','-')
 for uid,path in [(row['uid'],PRIMARY/(stem+'-provider.json')),(PODIUM,RELATION/'295538-0-primary.json')]:
  request=read(path.with_name(path.stem+'.request.json'));assert request['sha256']==digest(path.read_bytes()) and request['method']=='GET' and request['parameters']['outSR']=='2326' and request['parameters']['returnGeometry']=='true' and request['url'].endswith('/MapServer/0/query')
  providers[uid]=read(path)
 parent=next(b for b in read(PARENT_INPUT)['rows'] if b['uid']==PODIUM)
 return named_proof(previous,row,tri,[b for b,_,_ in forms],providers,parent)
