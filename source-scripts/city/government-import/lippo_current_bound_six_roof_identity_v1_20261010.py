"""Complete current binding for the named six original roof-edge identity role.

Only the two exact recorded current proxy foreign-area reasons are reconsidered.
All source/literal collision, support, terrain and installation gates are separate.
"""
import gzip,importlib.util,json
import numpy as np
import shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from tung_sing_current_bound_identity_20261010 import stream_pin
from lippo_three_original_current_inventory_20261010 import EXPECTED,native_rows,verify_native_rows,catalogue_inventory
from lippo_original_six_roof_current_scope_proposal_v2_20261010 import source_proof,OWN,FOREIGN,TOWER,ROLE_FACES,polygon,primary_polygon
DOC=ROOT/'docs/astra-city/government-import/government-xl-lippo-current-bound-six-roof-inputs-v1-20261010'
EXPECTED_RAW_REASONS=['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap']
PRIMARY_BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
PRIMARY_WHERE="BuildingCSUID IN ('3550417624P20050812','3551417531P20050812','3551817554T20050430')"
def module(name,filename):
 s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify_receipt(receipt,read_bytes=lambda p:p.read_bytes()):
 assert receipt['batch']==DOC.name and receipt['identityAccepted'] is False and receipt['newlyInstalled']==0
 assert len(receipt['evidenceRefs'])==len({r['path'] for r in receipt['evidenceRefs']})
 for r in receipt['evidenceRefs']:
  p=(ROOT/r['path']).resolve();assert p.is_relative_to(ROOT.resolve()) and digest(read_bytes(p))==r['sha256'],'Frozen evidence changed: '+r['path']
 return True

def primary_records(load=read,read_bytes=lambda p:p.read_bytes()):
 p=DOC/'exact-current-primary.json';request=load(DOC/'exact-current-primary.request.json');raw=read_bytes(p)
 params=dict(f='json',where=PRIMARY_WHERE,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
 assert request['method']=='GET' and request['url']==PRIMARY_BASE+'/0/query' and request['parameters']==params
 assert digest(raw)==request.get('decodedSHA256',request['sha256'])
 if request.get('gzipDecoded'):
  compressed=read_bytes(DOC/'exact-current-primary.provider-original.gz');assert digest(compressed)==request['sha256'] and gzip.decompress(compressed)==raw
 else:assert digest(raw)==request['sha256']
 obj=json.loads(raw);assert not obj.get('error') and not obj.get('exceededTransferLimit')
 assert obj['spatialReference'].get('latestWkid',obj['spatialReference'].get('wkid'))==2326
 assert len(obj['features'])==3 and {f['attributes']['BuildingCSUID'] for f in obj['features']}=={'3550417624P20050812','3551417531P20050812','3551817554T20050430'}
 return obj['features']

def current_binding(row,context,tri,capture,load_forms,read_bytes=lambda p:p.read_bytes()):
 before=read_bytes(ROOT/'3d-viewer/city/data/manifest.json');assert digest(before)==capture['manifestSHA256'],'Current manifest differs'
 lo,hi=tri.min((0,1)),tri.max((0,1));loaded=load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded]
 hashes={t:digest(read_bytes(ROOT/'3d-viewer'/t)) for _,_,t in loaded}
 assert hashes==context['neighbourTileHashes']==capture['tileHashes'] and forms==capture['forms'],'Complete current nearby forms/tiles changed'
 assert len(forms)==len({b['uid'] for b in forms}) and next(b for b in forms if b['uid']==OWN)==row['source']['building']
 sources=[];route={}
 for record in json.loads(before)['tiles']:
  raw=read_bytes(ROOT/'3d-viewer'/record['url']);matches=[b for b in json.loads(raw)['buildings'] if str(b.get('buildingCSUID') or '')[:10]==row['modelId'][1:11]]
  if matches:route[record['url']]=digest(raw);sources.extend(dict(building=b,tile=record['url'],tileSHA256=digest(raw)) for b in matches)
 assert route==capture['exactRouteTileHashes'],'Complete territory GeoRef route changed'
 inventory=catalogue_inventory(before,read_bytes);assert inventory==capture['catalogueInventory'],'Complete current catalogues changed'
 return forms,sources,inventory

def replay_raw(row,context,tri,capture,expected):
 final=module('lippo_full_raw_context_replay','xl-final-script-pass.py')
 loaded=[(b,final.form_polygon(b),next(t for t in context['neighbourTileHashes'] if t.endswith('/'+b['tile']+'.json'))) for b in capture['forms']]
 assert final.identity_context(row,tri,loaded)==context['identity'],'Raw complete context changed'
 from exact_original_georef_cell_identity_20261009 import verify_files as ordinary
 previous=ordinary(row,context,HERE/'local'/DOC.name/'raw-file-replay')
 assert previous['exactRouteTileHashes']==capture['exactRouteTileHashes'] and previous['exactRouteManifestSHA256']==capture['manifestSHA256']
 assert previous==expected and previous['reasons']==EXPECTED_RAW_REASONS and previous['passed'] is False,'Unknown or changed raw failure; no broad replacement'
 return previous

def projection(a):
 polys=shapely.polygons(a[:,:,[0,2]]);return shapely.union_all(polys[shapely.area(polys)>0])

def literal_measurements(originals,forms,primary,literal,bindings):
 assert len(literal['rows'])==3 and len({r['uid'] for r in literal['rows']})==3 and {r['uid'] for r in literal['rows']}==set(EXPECTED)
 actual={}
 for r in literal['rows']:
  assert r['loaderPassed'] and r['sourceSHA256']==EXPECTED[r['uid']][1]
  p=np.asarray(r['position'],dtype='<f8').reshape((-1,3));i=np.asarray(r['index'],dtype=np.int64).reshape((-1,3))
  assert np.isfinite(p).all() and i.min()>=0 and i.max()<len(p);a=p[i];pin=bindings[r['uid']]['literal']
  assert a.shape==originals[r['uid']].shape and len(a)==pin['completeFaces']==EXPECTED[r['uid']][2] and digest(a.tobytes())==pin['worldTrianglesSHA256']
  assert bindings[r['uid']]['original']==dict(completeFaces=len(originals[r['uid']]),worldTrianglesSHA256=digest(originals[r['uid']].astype('<f8').tobytes()))
  actual[r['uid']]=a
 # Original and literal role associations independently retain the complete
 # actual foreign surfaces. No source/actual arithmetic parity assumption.
 contacts=[]
 for own_kind,a in [('original',originals[OWN]),('literal',actual[OWN])]:
  role=a[sorted(ROLE_FACES)];normal=np.cross(role[:,1]-role[:,0],role[:,2]-role[:,0]);assert (normal[:,1]>0).all() and (normal[:,[0,2]]==0).all() and (role[:,:,1]==role[0,0,1]).all()
  for foreign_kind,b in [('original',originals[FOREIGN]),('literal',actual[FOREIGN])]:
   c=exact_finite_contacts(a,sorted(ROLE_FACES),b,range(len(b)))
   assert all(any(v['sourceFaceA']==f and v['dimension']==1 and v['sourcePrimitiveDimensionA']==v['sourcePrimitiveDimensionB']==2 for v in c['contacts']) for f in ROLE_FACES),'Exact current source/literal roof boundary association incomplete'
   contacts.append(dict(ownGeometry=own_kind,foreignGeometry=foreign_kind,completeSixRoofExactContacts=c))
 by={f['uid']:f for f in forms};features={p['attributes']['BuildingCSUID']:p for p in primary};measurements=[]
 for kind,a in [('original',originals[OWN]),('literal',actual[OWN])]:
  whole=projection(a);remaining=projection(a[[i for i in range(len(a)) if i not in ROLE_FACES]])
  for target_kind,target,named in [('current',polygon(by[OWN]['rings']),polygon(by[FOREIGN]['rings'])),('provider',primary_polygon(features['3551417531P20050812']),primary_polygon(features['3550417624P20050812']))]:
   assert target.intersection(named).area==0 and target.boundary.intersection(named.boundary).length>0
   extra=whole.difference(target);nonrole=remaining.difference(target)
   ordinary=shapely.union_all([extra.intersection(polygon(f['rings'])) for f in forms if f['uid'] not in [OWN,FOREIGN]])
   effective=shapely.union_all([ordinary,nonrole.intersection(named)])
   coverage=whole.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(a[:,:,[0,2]].reshape(-1,2)),target).max())
   assert coverage>=.95 and extent<=10 and effective.area<=1,'Complete source/literal ordinary spatial gate failed'
   measurements.append(dict(ownGeometry=kind,target=target_kind,fullTargetCoverage=float(coverage),fullMaximumSourceExtentM=extent,rawNamedForeignExcessM2=extra.intersection(named).area,allNonRoleNamedForeignExcessM2=nonrole.intersection(named).area,allOtherForeignExcessM2=ordinary.area,effectiveAllForeignExcessM2=effective.area))
 return dict(completeAllFourSpatialMeasurements=measurements,completeAllFourSourceLiteralExactRoleContacts=contacts)

def verify_files(row,context,local):
 assert row['uid']==OWN
 receipt=read(DOC/'result.json');verify_receipt(receipt);capture=read(DOC/'current-inputs.json.gz');lookup=read(DOC/'source-lookup.json.gz');selected=read(DOC/'selection.json.gz')['rows']
 assert len(selected)==3 and len({r['uid'] for r in selected})==3 and {r['uid'] for r in selected}==set(EXPECTED)
 selected={r['uid']:r for r in selected};assert selected[OWN]==row
 verify_native_rows(lookup['rows']);assert lookup['nativeRunID']==NATIVE_RUN
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  actual=native_rows(c);verify_native_rows(actual);assert actual==lookup['rows']
  for r in selected.values():
   assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
 sources_raw={};originals={};pins={};by={r['model']['modelId']:r for r in actual}
 for uid,(mid,sha,count) in EXPECTED.items():
  r=selected[uid];n=by[mid];assert n['model']==r['native']['model'] and n['sourceKey']==r['native']['cacheKey']+'/'+mid and n['resultSHA256']==r['native']['resultSha']
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==sha==r['sourceSHA256'];sources_raw[uid]=raw;originals[uid]=decode_original_world_triangles(raw);pins[uid]=stream_pin(raw,mid,count)
 assert pins==read(DOC/'complete-original-stream-pins.json.gz')
 final=module('lippo_complete_current_binding','xl-final-script-pass.py');forms,sources,inventory=current_binding(row,context,originals[OWN],capture,final.load_forms)
 literal=read(DOC/'literal-production-geometry.json.gz');inputs=read(DOC/'literal-source-inputs.json.gz')
 assert literal['completeProductionLoaderDependencyClosure'] and literal['unsupportedDynamicImports']==0 and literal['startAndEndInputHashesVerified']
 assert len(inputs['rows'])==3 and len({r['uid'] for r in inputs['rows']})==3
 for r in inputs['rows']:
  s=selected[r['uid']];assert r['entry']==s['candidate']['entry'] and r['building']==next(b for b in forms if b['uid']==r['uid']) and r['path']==s['candidate']['path']
 for p,h in literal['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,'Production loader/source binding changed: '+p
 primary=primary_records();previous=replay_raw(row,context,originals[OWN],capture,read(DOC/'raw-identity.json'))
 named=source_proof(sources_raw[OWN],sources_raw[FOREIGN],forms,primary)
 rendered=literal_measurements(originals,forms,primary,literal,read(DOC/'literal-complete-geometry-bindings.json.gz'))
 proof=dict(previous);proof.update(named);proof.update(rendered)
 proof.update(passed=True,reasons=[],identityAccepted=True,physicalAccepted=False,installationApproved=False,rawNativeIdentityReasons=previous['reasons'],rawFullCellIdentity=previous,namedIdentityOnlyReasonsReplaced=EXPECTED_RAW_REASONS,currentBinding=dict(manifestSHA256=capture['manifestSHA256'],completeCurrentTileHashes=capture['tileHashes'],completeCurrentCatalogueHashes=inventory['completeCatalogueHashes'],sourceEvidenceJobId=receipt['jobId'],allEvidenceRefsVerified=True,allOriginalStreamsVerified=True,threeUniqueCurrentNativeMembershipsVerified=True,completeLiteralRoleContactsVerified=True,rawFullCellRecomputed=True))
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==capture['manifestSHA256'] and catalogue_inventory((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==inventory
 assert all(digest((ROOT/'3d-viewer'/t).read_bytes())==h for t,h in capture['tileHashes'].items())
 return proof
