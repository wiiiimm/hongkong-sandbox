"""Complete current/source/provider binding for one named finite foreign silhouette.

Only the two recorded current footprint-proxy identity reasons are reconsidered.
No source/literal collision, terrain, support or foreign actor is exempted.
"""
import gzip,importlib.util,json
import numpy as np
import shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from routed_original_cell_identity import verify as routed_verify
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin
from one_peking_current_installed_foreign_inventory_20261010 import native_rows,verify_native_rows,installed_inventory
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import verify,OWN,FOREIGN,OWN_SHA,OWN_WORLD,FOREIGN_SHA,FOREIGN_WORLD,polygon,provider_polygon,projection
DOC=ROOT/'docs/astra-city/government-import/government-xl-one-peking-current-bound-installed-foreign-inputs-v1-20261010'
EXPECTED_RAW_REASONS=['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap']
PRIMARY_BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
PRIMARY_WHERE="BuildingCSUID IN ('3551217446P20050810','3553717452T20050430','3555317380P20090225')"
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
 assert len(obj['features'])==3 and {f['attributes']['BuildingCSUID'] for f in obj['features']}=={'3551217446P20050810','3553717452T20050430','3555317380P20090225'}
 return obj['features']
def current_binding(row,context,tri,capture,load_forms,read_bytes=lambda p:p.read_bytes()):
 before=read_bytes(ROOT/'3d-viewer/city/data/manifest.json');assert digest(before)==capture['manifestSHA256'],'Current manifest differs'
 lo,hi=tri.min((0,1)),tri.max((0,1));loaded=load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded]
 hashes={t:digest(read_bytes(ROOT/'3d-viewer'/t)) for _,_,t in loaded}
 assert hashes==context['neighbourTileHashes']==capture['tileHashes'] and forms==capture['forms'],'Complete current nearby forms/tiles changed'
 assert next(b for b in forms if b['uid']==OWN)==row['source']['building']
 sources=[];route={}
 for record in json.loads(before)['tiles']:
  raw=read_bytes(ROOT/'3d-viewer'/record['url']);matches=[b for b in json.loads(raw)['buildings'] if str(b.get('buildingCSUID') or '')[:10]==row['modelId'][1:11]]
  if matches:route[record['url']]=digest(raw);sources.extend(dict(building=b,tile=record['url'],tileSHA256=digest(raw)) for b in matches)
 assert route==capture['exactRouteTileHashes'],'Complete current territory GeoRef route changed'
 inventory=installed_inventory(before,read_bytes);assert inventory==capture['installedInventory'],'Complete installed catalogue/source routing changed'
 return forms,sources,inventory
def replay_raw(row,context,tri,raw,forms,sources,capture,expected):
 final=module('peking_complete_current_record','xl-final-script-pass.py');final.projection=lambda faces:shapely.union_all(shapely.polygons(np.asarray(faces)[:,:,[0,2]]))
 loaded=[(b,final.form_polygon(b),next(t for t in context['neighbourTileHashes'] if t.endswith('/'+b['tile']+'.json'))) for b in forms]
 current=final.identity_context(row,tri,loaded);assert current==context['identity'],'Raw full current geometry context differs'
 previous=routed_verify(raw,row,context,tri,current_identity=current,sources=sources)
 pin=dict(uid=OWN,sourceSHA256=OWN_SHA,decodedWorldTrianglesSHA256=OWN_WORLD)
 previous=apply_exact_cell(previous,tri,expected_binding=pin,current_binding=pin)
 previous.update(exactRouteTileHashes=capture['exactRouteTileHashes'],exactRouteManifestSHA256=capture['manifestSHA256'])
 assert previous==expected,'Complete raw full-cell identity changed'
 assert previous['reasons']==EXPECTED_RAW_REASONS and previous['passed'] is False,'Unknown or missing raw reason; no broad replacement'
 return previous
def literal_measurements(own,foreign,forms,primary,literal,bindings):
 assert len(literal['rows'])==2 and {r['uid'] for r in literal['rows']}=={OWN,FOREIGN}
 actual={}
 for r in literal['rows']:
  assert r['loaderPassed']
  p=np.asarray(r['position'],dtype='<f8').reshape((-1,3));i=np.asarray(r['index'],dtype=np.int64).reshape((-1,3))
  assert np.isfinite(p).all() and i.min()>=0 and i.max()<len(p)
  a=p[i];pin=bindings[r['uid']]['literal'];assert len(a)==pin['completeFaces'] and digest(a.tobytes())==pin['worldTrianglesSHA256']
  actual[r['uid']]=a
 by={b['uid']:b for b in forms};feature=next(f for f in primary if f['attributes']['BuildingCSUID']=='3551217446P20050810');measurements=[]
 for own_kind,a in [('original',own),('literal',actual[OWN])]:
  for foreign_kind,b in [('original',foreign),('literal',actual[FOREIGN])]:
   for target_kind,target in [('current',polygon(by[OWN]['rings'])),('provider',provider_polygon(feature))]:
    excess=projection(a).difference(target);total=shapely.union_all([excess.intersection(projection(b)),*[excess.intersection(polygon(f['rings'])) for f in forms if f['uid'] not in [OWN,FOREIGN]]])
    assert total.area<=1,(own_kind,foreign_kind,target_kind,total.area)
    measurements.append(dict(ownGeometry=own_kind,foreignGeometry=foreign_kind,target=target_kind,allForeignEffectiveExcessM2=total.area))
 return measurements
def verify_files(row,context,local):
 receipt=read(DOC/'result.json');verify_receipt(receipt);capture=read(DOC/'current-inputs.json.gz');lookup=read(DOC/'source-lookup.json.gz')
 verify_native_rows(lookup['rows']);assert lookup['nativeRunID']==NATIVE_RUN
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  actual=native_rows(c);verify_native_rows(actual);assert actual==lookup['rows']
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 assert actual[0]['sourceKey']==row['native']['cacheKey']+'/'+row['modelId'] and actual[0]['model']==row['native']['model'] and actual[0]['resultSHA256']==row['native']['resultSha']
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==OWN_SHA
 own=decode_original_world_triangles(raw);assert digest(own.astype('<f8').tobytes())==OWN_WORLD
 final=module('peking_complete_foreign_current_inventory','xl-final-script-pass.py');forms,sources,inventory=current_binding(row,context,own,capture,final.load_forms)
 f=inventory['installedForeign'];foreign_raw=(ROOT/f['assetPath']).read_bytes();assert digest(foreign_raw)==FOREIGN_SHA
 foreign=decode_original_world_triangles(foreign_raw);assert digest(foreign.astype('<f8').tobytes())==FOREIGN_WORLD
 pins=read(DOC/'complete-original-stream-pins.json.gz');assert pins=={OWN:stream_pin(raw,row['modelId'],4114),FOREIGN:stream_pin(foreign_raw,f['entry']['modelId'],32635)}
 literal=read(DOC/'literal-production-geometry.json.gz');source_inputs=read(DOC/'literal-source-inputs.json.gz')
 assert literal['completeProductionLoaderDependencyClosure'] and literal['unsupportedDynamicImports']==0 and literal['startAndEndInputHashesVerified']
 assert {r['uid']:r['sourceSHA256'] for r in literal['rows']}=={OWN:OWN_SHA,FOREIGN:FOREIGN_SHA}
 assert source_inputs['ownEntry']==row['candidate']['entry'] and source_inputs['foreignEntry']==f['entry']
 assert source_inputs['ownBuilding']==next(b for b in forms if b['uid']==OWN) and source_inputs['foreignBuilding']==next(b for b in forms if b['uid']==FOREIGN)
 for p,h in literal['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,'Production loader/source binding changed: '+p
 primary=primary_records();previous=replay_raw(row,context,own,raw,forms,sources,capture,read(DOC/'raw-identity.json'))
 named=verify(own,foreign,forms,primary,[f['entry']],OWN_SHA)
 proof=dict(previous);proof.update(named)
 measurements=literal_measurements(own,foreign,forms,primary,literal,read(DOC/'literal-complete-geometry-bindings.json.gz'))
 proof.update(passed=True,reasons=[],rawNativeIdentityReasons=previous['reasons'],rawFullCellIdentity=previous,namedIdentityOnlyReasonsReplaced=EXPECTED_RAW_REASONS,
  literalCompleteAllEightCombinations=measurements,currentBinding=dict(manifestSHA256=capture['manifestSHA256'],completeCurrentTileHashes=capture['tileHashes'],completeCurrentCatalogueHashes=inventory['completeCatalogueHashes'],sourceEvidenceJobId=receipt['jobId'],allEvidenceRefsVerified=True,allOriginalStreamsVerified=True,completeCurrentOwnNativeMembershipVerified=True,uniqueInstalledForeignCompleteSourceVerified=True,rawFullCellRecomputed=True),identityAccepted=True,physicalAccepted=False,collisionExemption=False,installationApproved=False)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==capture['manifestSHA256']
 assert all(digest((ROOT/'3d-viewer'/t).read_bytes())==h for t,h in capture['tileHashes'].items())
 return proof
