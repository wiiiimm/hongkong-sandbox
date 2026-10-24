"""ROOT-only cached-original proposal. No import/preflight model math/DB.
Normal preparation/calculation require an external maintained canonical lease.
No claim/release/freezer/acceptance is performed by this caller.
"""
import argparse,gzip,hashlib,json,os,struct,sys,time
from pathlib import Path
PACKET=Path(__file__).resolve().parent;ROOT=PACKET.parents[3]
HERE=ROOT/'source-scripts/city/government-import';CONTRACT=PACKET/'input-contract.json'
ARRAYS=PACKET/'cached-complete-original-arrays-v1';OUTPUT=PACKET/'two-original-scope-interface-output-v1';TARGET_AUDIT=PACKET/'exact-provider-target-audit-output-v1'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(p,v):
 raw=json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 with p.open('xb') as f:f.write(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw+b'\n')
def fence(c,cs):
 assert sha(CONTRACT)==cs and sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 for rel,value in c['filePins'].items():assert sha(ROOT/rel)==value,rel
 assert sha(Path(__file__))==c['callerSHA256']
def metadata(c):
 provider=read(ROOT/c['providerFeaturesPath']);forms=read(ROOT/c['currentFormsPath'])['forms'];by_uid={f['uid']:f for f in forms}
 assert len(forms)==6 and len(by_uid)==6
 result=[]
 for s in c['sourceTuples']:
  matches=[f for f in provider['featuresVerbatim'] if f['properties']['BuildingCSUID']==s['CSUID']];assert len(matches)==1
  f=matches[0];b=by_uid[s['uid']];a=f['properties']
  assert b['objectId']==a['OBJECTID'] and b['buildingCSUID']==a['BuildingCSUID'] and b['structureType']==a['BuildingBlockType'] and a['Status']=='Active'
  assert f['geometry']['type']=='Polygon' and len(f['geometry']['coordinates'])==len(b['rings'])==1
  assert len(f['geometry']['coordinates'][0])==len(b['rings'][0])==s['providerRingVertices']
  result.append({'uid':s['uid'],'providerAttributesVerbatim':a,'providerOriginalGeometryVerbatim':f['geometry'],'currentFormVerbatim':b,'integrationCodeInspectionFact':'OSM names/parent/refs are attached; official rings are not replaced. This is code provenance, not a fresh coordinate-equivalence predicate.','currentNameDerivedFromOSM':a['BuildingNameEN'] is None and bool(b['name'])})
 return result,forms
def maintained_lease(c,path):
 assert path is not None
 sys.path.insert(0,str(HERE));from run import reservations
 lease=read(path);assert lease['resources']==c['canonicalResources'] and reservations.owns(lease)
 last=time.monotonic()
 def heartbeat(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   value=reservations.heartbeat(lease,ttl=3600);assert value['ok'],value;last=time.monotonic()
 heartbeat(True);return reservations,lease,heartbeat
def main():
 parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
 for flag in ('preflight-only','audit-provider-target-only','prepare-cached-original-arrays-only','calculate-two-original-context-only'):group.add_argument('--'+flag,action='store_true')
 parser.add_argument('--lease-file',type=Path);parser.add_argument('--array-receipt-sha256');args=parser.parse_args();assert bool(args.calculate_two_original_context_only)==bool(args.array_receipt_sha256);c=read(CONTRACT);cs=sha(CONTRACT);fence(c,cs);records,forms=metadata(c)
 if args.preflight_only:
  assert args.lease_file is None and not ARRAYS.exists() and not OUTPUT.exists() and not TARGET_AUDIT.exists()
  fence(c,cs);print(json.dumps({'passed':True,'providerTargetRecords':records,'rawPodiumProviderNameNull':records[1]['providerAttributesVerbatim']['BuildingNameEN'] is None,'canonicalResources':c['canonicalResources'],'sourceArraysNotYetDecoded':True,'noDB':True,'noLease':True,'identityAccepted':False}));return
 reservations,lease,heartbeat=maintained_lease(c,args.lease_file)
 import numpy as np
 if args.audit_provider_target_only:
  assert not TARGET_AUDIT.exists();TARGET_AUDIT.mkdir()
  import importlib.util
  from pyproj import Transformer
  from shapely.geometry import Polygon
  spec=importlib.util.spec_from_file_location('hkust_existing_provider_polygon_protocol',ROOT/c['existingPolygonProtocolPath']);build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
  assert list(build.ORIGIN)==[834500,816500]
  transform=Transformer.from_crs(4326,2326,always_xy=True);audits=[]
  features=read(ROOT/c['providerFeaturesPath'])['featuresVerbatim']
  for record in records:
   feature=next(f for f in features if f['properties']['BuildingCSUID']==record['providerAttributesVerbatim']['BuildingCSUID']);rings=[]
   for ring in feature['geometry']['coordinates']:
    east,north=transform.transform(*zip(*[point[:2] for point in ring]));rings.append(list(map(list,zip(east,north))))
   geometry,repaired=build.official_geometry({'attributes':feature['properties'],'geometry':{'rings':rings}})
   parts=list(build.polys(geometry));assert len(parts)==1
   packed=build.pack(parts[0]);current=record['currentFormVerbatim']['rings']
   # Exact output of the existing converter, no distance/area tolerance waiver.
   audits.append({'uid':record['uid'],'providerCSUID':feature['properties']['BuildingCSUID'],'providerObjectID':feature['properties']['OBJECTID'],'providerSourceRingsVerbatim':feature['geometry']['coordinates'],'existingConversionPackedWorldRings':packed,'currentFormRingsVerbatim':current,'literalPackedRingsEqualCurrent':packed==current,'providerShapeAreaM2':feature['properties']['Shape_Area'],'convertedUnpackedAreaM2':parts[0].area,'convertedPackedAreaM2':Polygon(packed[0],packed[1:]).area,'geometryRepairByExistingProtocol':repaired,'currentGeometryRepairFlag':record['currentFormVerbatim']['geometryRepaired'],'providerNameEN':feature['properties']['BuildingNameEN'],'currentName':record['currentFormVerbatim']['name'],'currentParent':record['currentFormVerbatim'].get('parent'),'identityAccepted':False})
  heartbeat(True);fence(c,cs);assert reservations.owns(lease)
  save(TARGET_AUDIT/'target-audit.json',{'records':audits,'allInputHashesUnchanged':True,'currentAcceptance':False,'noModelDecode':True,'noCoverageGuardChanged':True,'sourceGeometryChanges':0})
  print(json.dumps({'complete':True,'targetAuditSHA256':sha(TARGET_AUDIT/'target-audit.json'),'literalRingMatches':[{'uid':r['uid'],'matched':r['literalPackedRingsEqualCurrent']} for r in audits],'currentAcceptance':False}));return
 if args.prepare_cached_original_arrays_only:
  assert not ARRAYS.exists() and not OUTPUT.exists();ARRAYS.mkdir()
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  from xl_source_stream_binding_20261009 import source_stream_binding
  rows=[]
  for s in c['sourceTuples']:
   heartbeat();raw=(ROOT/s['originalAssetPath']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['sourceSHA256']
   tri=decode_original_world_triangles(raw);assert tri.shape==(s['originalFaces'],3,3) and np.isfinite(tri).all()
   world=hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest()
   if s['uid']=='landsd/309822:0':assert world==s['priorOriginalWorldSHA256']
   # P world SHA is new canonical decode evidence; no historical hash invented.
   name=s['uid'].replace('/','-').replace(':','-')+'.json.gz';file=ARRAYS/name
   save(file,{'sourceTuple':s,'completeSourceStreamBinding':source_stream_binding(raw),'originalWorldSHA256':world,'completeOrderedOriginalTriangles':tri.tolist(),'completeOriginalFaces':len(tri),'sourceGeometryChanges':0})
   rows.append({'uid':s['uid'],'path':str(file.relative_to(ROOT)),'sha256':sha(file),'originalWorldSHA256':world,'sourceSHA256':s['sourceSHA256'],'completeFaces':len(tri)})
  heartbeat(True);fence(c,cs);assert reservations.owns(lease)
  save(ARRAYS/'array-receipt.json',{'rows':rows,'decoderSHA256':sha(HERE/'exact_packed_world_geometry_20261009.py'),'inputContractSHA256':cs,'allInputHashesUnchanged':True,'originalPoseChanges':0,'sourceGeometryChanges':0,'currentAcceptance':False})
  print(json.dumps({'complete':True,'arrayReceiptSHA256':sha(ARRAYS/'array-receipt.json'),'rows':rows,'currentAcceptance':False}));return
 assert ARRAYS.exists() and not OUTPUT.exists();assert sha(ARRAYS/'array-receipt.json')==args.array_receipt_sha256,'ROOT observed array receipt must be pinned';receipt=read(ARRAYS/'array-receipt.json');assert len(receipt['rows'])==2 and receipt['inputContractSHA256']==cs and receipt['decoderSHA256']==sha(HERE/'exact_packed_world_geometry_20261009.py')
 triangles={};array_refs=[]
 for row,s in zip(receipt['rows'],c['sourceTuples']):
  assert row['uid']==s['uid'] and row['sourceSHA256']==s['sourceSHA256'];f=ROOT/row['path'];assert sha(f)==row['sha256'];a=read(f);assert a['sourceTuple']==s
  tri=np.asarray(a['completeOrderedOriginalTriangles'],dtype='<f8');assert tri.shape==(s['originalFaces'],3,3) and np.isfinite(tri).all() and hashlib.sha256(tri.tobytes()).hexdigest()==row['originalWorldSHA256']
  triangles[s['uid']]=tri;array_refs.append({'path':row['path'],'sha256':row['sha256']})
 OUTPUT.mkdir()
 from shapely.geometry import MultiPoint,Polygon
 from shapely import union_all
 from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,primitive_census
 from exact_finite_contact_crossing_classification_20261011 import classify
 sys.path.insert(0,str(PACKET));from hkust_original_lower_level_edge_context_draft_v1 import lower_level_edge_context
 uids=[s['uid'] for s in c['sourceTuples']];t,p=(triangles[u] for u in uids)
 projections={u:union_all([MultiPoint(face[:,[0,2]]).convex_hull for face in tri]) for u,tri in triangles.items()}
 # All projected ranks retained; GEOS scope measurement, not physical proof.
 tile_forms=read(ROOT/c['currentTilePath'])['buildings']
 min_x=min(float(tri[:,:,0].min()) for tri in triangles.values());max_x=max(float(tri[:,:,0].max()) for tri in triangles.values())
 min_z=min(float(tri[:,:,2].min()) for tri in triangles.values());max_z=max(float(tri[:,:,2].max()) for tri in triangles.values())
 # Exact comparisons of stored finite doubles; strict-disjoint exclusions only.
 # Raw-ring scope only, not actual BASIC/native mesh collision separation.
 nominated=[];excluded=[]
 for f in tile_forms:
  points=[point for ring in f['rings'] for point in ring]
  closed=[min(q[0] for q in points),min(q[1] for q in points),max(q[0] for q in points),max(q[1] for q in points)]
  (excluded if closed[2]<min_x or closed[0]>max_x or closed[3]<min_z or closed[1]>max_z else nominated).append({'form':f,'bounds':closed})
 assert len(nominated)+len(excluded)==len(tile_forms)
 scoped_forms=[r['form'] for r in nominated]
 assert set(uids).issubset({f['uid'] for f in scoped_forms})
 targets={f['uid']:Polygon(f['rings'][0],f['rings'][1:]) for f in scoped_forms}
 assert all(poly.is_valid and not poly.is_empty and poly.area>0 for poly in targets.values()),'Preserve invalid current polygon; do not silently repair'
 assembly=union_all([targets[u] for u in uids]);joint=union_all([projections[u] for u in uids])
 scope=[]
 for label,projection,target in [(u,projections[u],targets[u]) for u in uids]+[('tower-only-against-expanded-target',projections[uids[0]],assembly),('two-originals-against-expanded-target',joint,assembly)]:
  excess=projection.difference(target)
  scope.append({'label':label,'targetAreaM2':target.area,'sourceProjectionAreaM2':projection.area,'targetCoverage':target.intersection(projection).area/target.area,'sourceExcessAreaM2':excess.area,'completeIndependentOverlapRows':[{'uid':f['uid'],'CSUID':f.get('buildingCSUID'),'parent':f.get('parent'),'name':f['name'],'sourceProjectionOverlapAreaM2':projection.intersection(targets[f['uid']]).area,'sourceExcessOverlapAreaM2':excess.intersection(targets[f['uid']]).area} for f in scoped_forms if f['uid'] not in uids],'qualification':'GEOS projection diagnostic only; no missing-area architectural role or identity approval.'})
 save(OUTPUT/'complete-projection-scope.json',scope);heartbeat(True)
 # Mathematical full Cartesian bound, not an arbitrary resource ceiling.
 contacts=exact_finite_contacts(t,list(range(len(t))),p,list(range(len(p))),maximum_pairs=len(t)*len(p))
 for row in contacts['contacts']:row['exactCrossingClassification']=classify(t[row['sourceFaceA']],p[row['sourceFaceB']],row)
 save(OUTPUT/'complete-finite-interfaces.json.gz',contacts);heartbeat(True)
 lower=lower_level_edge_context(t,p,heartbeat);save(OUTPUT/'complete-minimum-level-edge-context.json.gz',lower)
 out={'uids':uids,'sourceTuples':c['sourceTuples'],'priorExactSourceJobs':c['priorExactSourceJobs'],'providerTargetProvenance':records,'currentAllSixFormsVerbatim':forms,'completeCurrentTileRawRingNomination':{'sourceClosedBounds':[min_x,min_z,max_x,max_z],'nominated':nominated,'strictDisjointExclusions':excluded,'completeTileForms':len(tile_forms),'qualification':'Raw-ring footprint scope only; no full unused actual native/BASIC separation or physical credit.'},'projectionScope':scope,'completeOriginalPrimitiveAccounts':{u:primitive_census(tri) for u,tri in triangles.items()},'arrayRefs':array_refs,'interfaceResult':{'path':str((OUTPUT/'complete-finite-interfaces.json.gz').relative_to(ROOT)),'sha256':sha(OUTPUT/'complete-finite-interfaces.json.gz'),'records':len(contacts['contacts']),'trianglePairsTested':contacts['trianglePairsTested'],'fullPairBound':len(t)*len(p)},'lowerEdgeResult':{'path':str((OUTPUT/'complete-minimum-level-edge-context.json.gz').relative_to(ROOT)),'sha256':sha(OUTPUT/'complete-minimum-level-edge-context.json.gz'),'completeEdges':len(lower['completeMinimumLevelNonzeroEdges']),'withoutCompleteExactContact':lower['wholeEdgesWithoutCompleteExactContact']},'all227OldInterfaceNegativesVerbatim':read(ROOT/c['priorBindingsPath'])['historicalInterfaceRowVerbatim'],'towerOnlyExpandedTargetFailureVerbatim':read(ROOT/c['priorBindingsPath'])['historicalTowerGroupRoleVerbatim']['variants'],'noSourceComponentCensus':True,'noCurrentFourWorldPhysicalProof':True,'noStructuralSupportCredit':True,'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'newlyInstalled':0}
 heartbeat(True);fence(c,cs);assert reservations.owns(lease)
 for ref in array_refs:assert sha(ROOT/ref['path'])==ref['sha256']
 save(OUTPUT/'result.json',out);save(OUTPUT/'terminal.json',{'complete':True,'resultSHA256':sha(OUTPUT/'result.json'),'inputContractSHA256':cs,'allInputHashesUnchanged':True,'currentAcceptance':False,'noGeometryChanges':True,'workerPID':os.getpid()})
 print(json.dumps({'complete':True,'resultSHA256':sha(OUTPUT/'result.json'),'contactRecords':len(contacts['contacts']),'lowerEdges':len(lower['completeMinimumLevelNonzeroEdges']),'currentAcceptance':False}))
if __name__=='__main__':main()
