"""Complete unchanged installed236490 source versus current/proposed terrain.
Four full indexed streams and all unused POSITION vertices stay distinct. This
preserves a legacy installed actor, not new whole-building support approval.
"""
import importlib.util,json,subprocess,shutil,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011';PHYS=BASE/'government-xl-vancor-basic-parent-core-apron-current-physical-v3-20261011'
BATCH='government-xl-vancor-retained-upper-complete-current-regression-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;JS=HERE/'xl-vancor-retained-upper-actual-render-geometry-v1-20261011.mjs';UID='landsd/236490:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not LOCAL.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert read(PHYS/'diagnostic.json')['currentManifest']==start;refs=[Path(__file__),JS,manifest]
 for folder in [INPUT,PHYS]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(folder/'result.json')
 proposal=read(INPUT/'proposal-input.json');forms=read(INPUT/'complete-proposed-region-current-forms.json.gz')['rows'];form=next(r['building']for r in forms if r['building']['uid']==UID);matches=[]
 for cr in proposal['completeCurrentCatalogueRefs']:
  cp=ROOT/cr['path'];assert ref(cp)==cr
  for e in read(cp)['models']:
   if e['uid']==UID:matches.append((cp,e))
 assert len(matches)==1;cp,entry=matches[0];asset=cp.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']and entry['triangles']==840 and entry['buildingCSUID']==form['buildingCSUID'];source=decode_original_world_triangles(asset.read_bytes());assert source.shape==(840,3,3)
 tile=next(p for p in proposal['completeCurrentTileHashes']if any(b['uid']==UID for b in read(ROOT/p)['buildings']));assert next(b for b in read(ROOT/tile)['buildings']if b['uid']==UID)==form
 claim=reservations.claim('vancor-retained-upper-preservation-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir(parents=True);LOCAL.mkdir(parents=True);pins=[ref(p)for p in [manifest,cp,asset,ROOT/tile,JS,Path(__file__)]]
  def call(args,label):
   p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/(label+'-log.json'),dict(args=args,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr;assert reservations.owns(lease)and all(ref(ROOT/r['path'])==r for r in pins)
  call(['node',str(JS)],'actual-render');actual=read(DOC/'complete-actual-render-geometry.json.gz');assert actual['startAndEndInputsVerified']and len(actual['rows'])==1;a=actual['rows'][0];assert a['uid']==UID and a['sourceSHA256']==entry['sha256']and a['completeFaces']==840
  destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,destination);assert digest(destination.read_bytes())==entry['sha256'];selection=dict(batch=BATCH,manifestSHA256=start['sha256'],rows=[dict(uid=UID,sourceSHA256=entry['sha256'],source=dict(building=form,tile=tile.removeprefix('3d-viewer/')),candidate=dict(path=str(destination.relative_to(ROOT)),entry=entry))]);save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',read(PHYS/'terrain-candidates.json'))
  idx=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);streams={'providerOriginal':source};positions={}
  for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:positions[mode]=np.asarray(a[key],dtype='<f8').reshape(-1,3);streams[mode]=positions[mode][idx]
  packed=packed_world_bounds(asset.read_bytes());assert packed['allOriginalPositionVerticesAccounted']and all(len(p)==packed['completeOriginalPositionVertices']for p in positions.values())
  command=['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT))]
  for phase in ['before','after']:
   args=command+['--out',str((DOC/(phase+'-metrics.json')).relative_to(ROOT)),'--geometry-out',str((DOC/(phase+'-runtime-geometry.json.gz')).relative_to(ROOT))]
   if phase=='after':args+=['--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT))]
   call(args,phase)
  runtimes={phase:read(DOC/(phase+'-runtime-geometry.json.gz'))for phase in ['before','after']};grounds={};cache={};results=[]
  for phase,runtime in runtimes.items():
   assert len(runtime['rows'])==1;rt=runtime['rows'][0];assert rt['uid']==UID and rt['sourceSHA256']==entry['sha256']and rt['index']==a['completeOriginalIndex']and np.array_equal(np.asarray(rt['position']),np.asarray(a['completeLiteralWorldPosition']));grounds[phase]=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
   for mode,world in streams.items():
    faces=[]
    for i,face in enumerate(world):
     key=(digest(face.tobytes()),digest(grounds[phase].tobytes()))
     if key not in cache:
      first=coarse(face,grounds[phase]);second=None if first['existingOrdinaryClearanceBoundProved']else paired(face,grounds[phase]);cache[key]=dict(coarse=first,paired=second,ordinaryFiniteClear=first['existingOrdinaryClearanceBoundProved']or bool(second and second['existingOrdinaryClearanceBoundProved']))
     faces.append(dict(sourceFace=i,**cache[key]))
    results.append(dict(phase=phase,arithmetic=mode,completeSourceWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(grounds[phase].tobytes()),completeSourceFaces=840,completeGroundFaces=len(grounds[phase]),all840FiniteFaceProofs=faces,unprovedFiniteFaces=[f['sourceFace']for f in faces if not f['ordinaryFiniteClear']]))
  metrics={phase:read(DOC/(phase+'-metrics.json'))for phase in ['before','after']};assert all(len(v['rows'])==1 and not v['rows'][0].get('error')for v in metrics.values());old=np.asarray(runtimes['before']['rows'][0]['drawnGround']);new=np.asarray(runtimes['after']['rows'][0]['drawnGround']);assert len(old)==len(new)==len(positions['actualLiteral'])and np.isfinite(old).all()and np.isfinite(new).all()
  out=dict(uid=UID,currentManifest=start,unchangedInstalledEntry=entry,unchangedInstalledAsset=ref(asset),completeOriginalPOSITIONProof=packed,completeActualAttributesMatrices=ref(DOC/'complete-actual-render-geometry.json.gz'),completeLiteralUnusedVertexTerrainBefore=old.tolist(),completeLiteralUnusedVertexTerrainAfter=new.tolist(),maximumLiteralVertexGroundChangeM=float(np.max(np.abs(new-old))),fullBeforeAndAfterFourStream840FaceProofs=results,allBeforeAndAfterWholeFacetsOrdinaryFiniteClear=all(not r['unprovedFiniteFaces']for r in results),legacySourceSupportNotReapproved=True,legacyBottomRimFlagsPreserved={phase:v['rows'][0]for phase,v in metrics.items()},sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False)
  save(DOC/'diagnostic.json.gz',out)
  for capture in [actual,*runtimes.values(),*metrics.values()]:
   for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
  refs += [cp,asset,ROOT/tile,INPUT/'proposal-input.json',INPUT/'complete-proposed-region-current-forms.json.gz',PHYS/'terrain-candidates.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']+[p for p in DOC.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()]
  assert ref(manifest)==start and reservations.owns(lease)
  s=importlib.util.spec_from_file_location('vancor_retained_upper_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-current-retained-upper840-faces-all-four-worlds-before-after-finite-terrain-diagnostic-no-legacy-reapproval',refs,dict(uids=[UID],allBeforeAndAfterWholeFacetsOrdinaryFiniteClear=out['allBeforeAndAfterWholeFacetsOrdinaryFiniteClear'],currentAcceptance=False,newlyInstalled=0))
  print(json.dumps(dict(allBeforeAndAfterWholeFacetsOrdinaryFiniteClear=out['allBeforeAndAfterWholeFacetsOrdinaryFiniteClear'],maximumLiteralVertexGroundChangeM=out['maximumLiteralVertexGroundChangeM'])),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
