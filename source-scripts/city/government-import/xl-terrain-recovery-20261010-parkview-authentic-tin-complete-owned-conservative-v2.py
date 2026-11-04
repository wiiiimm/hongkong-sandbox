"""Parkview complete OWNED source-only AUTHENTIC TIN comparison; no terrain publication.

No import acceptance is granted. Every actual original and rendered triangle
gets exact projection coverage and a separate conservative finite height bound.
"""
import argparse,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
from original_complete_conservative_clearance_cache_20261010 import reuse,canonical
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--reuse',action='append',default=[]);p.add_argument('--physical',required=True);p.add_argument('--batch',required=True);a=p.parse_args();doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();physical=ROOT/a.physical;geometry=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(geometry);selection=read(physical/'selection.json.gz');rows=[];refs=[ref(p) for p in [Path(__file__),geometry,physical/'selection.json.gz',physical/'result.json',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'test_exact_projection_coverage_v2_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']]
 baseline=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-park-hkdi-current-source-scope-v1/historical-current-manifest.json';assert digest(baseline.read_bytes())=='afe71ffa851d82ab2d1350834b5a6cd1484f28e481bd6bf866ca7a6f73e05d0b'
 parent_entry=next(x for x in read(baseline)['terrainPatches']if x['url']=='city/data/government-native-255439-0.json');parent_path=ROOT/'3d-viewer'/parent_entry['url'];assert digest(parent_path.read_bytes())==parent_entry['sha256']
 native_source=next(x for x in parent_entry['source']['nativeSources']if x['sheet']=='11-SE-21B');sourcefiles=[ROOT/x['path']for x in native_source['sourceFiles']]
 for pin in native_source['sourceFiles']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 gltf=next(x for x in sourcefiles if x.suffix=='.gltf');spec=importlib.util.spec_from_file_location('parkview_authentic_terrain_decoder',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);authentic_full=context.triangles(gltf);assert len(authentic_full)==253144
 refs.extend(ref(p)for p in [baseline,parent_path,*sourcefiles,HERE/'pending-context.py',HERE.parent/'citywide-native/convert.py',ROOT/'docs/astra-city/mui-wo-buildings/review/prepare_model_sample.py',ROOT/'docs/astra-city/mui-wo-buildings/review/bake_model_geometry.py'])
 assert {x['uid']for x in selection['rows']}=={'landsd/255647:0','landsd/254491:0'}
 selection={**selection,'rows':[x for x in selection['rows']if x['uid']=='landsd/255647:0']}
 legacy=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-parkview-block11-complete-original-and-literal-finite-v1/diagnostic.json.gz';refs.extend([ref(legacy),ref(HERE/'xl-terrain-recovery-20261010-parkview-authentic-tin-complete-conservative-v1.py')])
 failure=Path('/tmp/parkview-authentic-tin-complete-conservative-v1-20261010.log');failure_bytes=failure.read_bytes();assert b'Missing finite drawn-ground projection'in failure_bytes;failed_copy=doc/'prior-native-comparison-failed-v1.log';failed_copy.parent.mkdir(parents=True,exist_ok=True);failed_copy.write_bytes(failure_bytes);refs.append(ref(failed_copy))
 cached_rows={};cache_refs=[]
 for name in a.reuse:
  folder=ROOT/name;receipt=read(folder/'result.json');report=read(folder/'diagnostic.json.gz')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert any(r==ref(folder/'diagnostic.json.gz') for r in receipt['evidenceRefs'])
  for file in ['exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py']:
   assert ref(HERE/file) in receipt['evidenceRefs'],'Cached numerical producer kernel changed'
  cache_refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
  for cached in report['rows']:
   assert cached['uid'] not in cached_rows;cached_rows[cached['uid']]=cached
 refs.extend(cache_refs);refs.extend(ref(HERE/n) for n in ['original_complete_conservative_clearance_cache_20261010.py','test_original_complete_conservative_clearance_cache_20261010.py'])
 claim=reservations.claim('complete-conservative-clearance-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  for row in reversed(selection['rows']):
   asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);world=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
   captured_ground=ground;captured_ground_sha=digest(captured_ground.tobytes());wholepositions=np.concatenate([tri.reshape(-1,3),world.reshape(-1,3),np.asarray(r['position'],float).reshape(-1,3)]);lo=wholepositions[:,[0,2]].min(axis=0);hi=wholepositions[:,[0,2]].max(axis=0);ids=np.flatnonzero(np.all(authentic_full[:,:,[0,2]].max(axis=1)>=lo,axis=1)&np.all(authentic_full[:,:,[0,2]].min(axis=1)<=hi,axis=1));ground=authentic_full[ids];assert len(ground)
   if row['uid'] in cached_rows:
    cached=cached_rows[row['uid']];rows.append(reuse(cached,row['sourceSHA256'],tri,world,ground,expected_cached_sha=canonical(cached)));refs.append(ref(asset));print(json.dumps(dict(uid=row['uid'],completeImmutableFacesReused=len(tri),allSourceWorldGroundHashesEqual=True)),flush=True);continue
   assert not a.reuse,'Changed authentic terrain baseline cannot reuse captured-current-ground results'
   checkpoint=HERE/'local'/a.batch/(row['uid'].replace('/','-').replace(':','-')+'-partial.json.gz');binding=dict(producer=ref(Path(__file__)),physicalReceipt=ref(physical/'result.json'),runtime=ref(geometry),sourceSHA256=row['sourceSHA256'],originalWorldSHA256=digest(tri.tobytes()),renderedWorldSHA256=digest(world.tobytes()),groundSHA256=digest(ground.tobytes()),kernels=[ref(HERE/n) for n in ['exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py']]);partial=read(checkpoint) if checkpoint.exists() else None;assert partial is None or partial['binding']==binding;faces=[] if partial is None else partial['faces'];assert [r['sourceFace'] for r in faces]==list(range(len(faces))) and len(faces)<=len(tri)
   for i in range(len(faces),len(tri)):
    original,rendered=tri[i],world[i]
    first=verify(original,ground);second=first if np.array_equal(original,rendered) else verify(rendered,ground);faces.append(dict(sourceFace=i,completeOriginal=first,actualRendered=second))
    if i%200==0:save(checkpoint,dict(binding=binding,faces=faces,complete=False));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(uid=row['uid'],completeFacesChecked=i,total=len(tri))),flush=True)
   save(checkpoint,dict(binding=binding,faces=faces,complete=True));refs.append(ref(asset));rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),capturedCurrentGroundSHA256=captured_ground_sha,authenticWholeSourceTerrainTriangles=253144,authenticWholeSourceTerrainSHA256=digest(authentic_full.tobytes()),authenticSelectedWholeFacetIds=ids.tolist(),authenticTerrainSelectionClosedBounds=[lo.tolist(),hi.tolist()],comparisonGroundIsAuthenticatedOriginalTINNotCurrentRenderedTerrain=True,completeOriginalFaces=len(tri),allFaces=faces,unprovedOriginalFaceBounds=[r['sourceFace'] for r in faces if not r['completeOriginal']['existingOrdinaryClearanceBoundProved']],unprovedActualRenderedFaceBounds=[r['sourceFace'] for r in faces if not r['actualRendered']['existingOrdinaryClearanceBoundProved']]))
  result=dict(rows=rows,allWholeOriginalAndRenderedBoundsProved=all(not r['unprovedOriginalFaceBounds'] and not r['unprovedActualRenderedFaceBounds'] for r in rows),rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,comparisonGround='authenticated complete 11-SE-21B original TIN; not a current rendered terrain or accepted proposal',terrainProposalPublished=False,freshCurrentAcceptance=False,nativeReacceptance=False,wholeRetainedNativeOriginalLiteralDiagnosticsPreserved=ref(legacy),nativeAuthenticTerrainComparisonStillUnresolved=True,priorNativeMissingFacetFailurePreserved=ref(failed_copy),historicalManifestAlias=dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(baseline.read_bytes()),archive=ref(baseline)),fullAcceptance=False,installationApproved=False,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('conservative_clearance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'parkview-complete-owned-original-literal-authenticated-TIN-conservative-comparison-v2',[*[ROOT/r['path'] for r in refs],doc/'diagnostic.json.gz'],dict(uids=[r['uid'] for r in rows],completeOriginalFaces=sum(r['completeOriginalFaces'] for r in rows),allWholeOriginalAndRenderedBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedFaces={r['uid']:r['unprovedOriginalFaceBounds'] for r in rows},rawPriorDiagnosticChanged=False,fullAcceptance=False))
  print(json.dumps(dict(allWholeOriginalAndRenderedBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedOriginalCounts={r['uid']:len(r['unprovedOriginalFaceBounds']) for r in rows},unprovedLiteralCounts={r['uid']:len(r['unprovedActualRenderedFaceBounds']) for r in rows},freshCurrentAcceptance=False,nativeReacceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
