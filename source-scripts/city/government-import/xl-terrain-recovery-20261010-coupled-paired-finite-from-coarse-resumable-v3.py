"""Source-only exact paired refinement with immutable Neon-fenced face chunks.

Same frozen exact finite mathematics and -0.5m limit as the earlier v1 runner.
Resume only previously complete, hash-pinned, fenced numerical chunks. No terrain,
source edits, support/root credit, native reacceptance or installation approval.
"""
import argparse,importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_20261010 import verify
from original_paired_finite_chunk_accounting_20261010 import verify_chunk

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fenced(folder):
 result=read(folder/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for r in result['evidenceRefs']:assert ref(ROOT/r['path'])==r
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--physical',required=True);p.add_argument('--clearance',required=True);p.add_argument('--batch',required=True);p.add_argument('--baseline-manifest',required=True);p.add_argument('--chunk-faces',type=int,default=512);p.add_argument('--max-new-chunks',type=int);a=p.parse_args()
 assert 1<=a.chunk_faces<=4096 and (a.max_new_chunks is None or a.max_new_chunks>0)
 physical=ROOT/a.physical;old=ROOT/a.clearance;base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists()
 receipt=fenced(old);prior=read(old/'diagnostic.json.gz');assert ref(old/'diagnostic.json.gz')in receipt['evidenceRefs']
 geometry=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(geometry);selection=read(physical/'selection.json.gz')
 baseline=ROOT/a.baseline_manifest;baseline_raw=baseline.read_bytes();baseline_sha=digest(baseline_raw)
 assert selection['manifestSHA256']==baseline_sha,'Exact frozen captured baseline required; no fresh-current claim'
 baseline_folder=base/(a.batch+'-frozen-baseline');baseline_archive=baseline_folder/'historical-captured-ground-manifest.json'
 if baseline_archive.exists():assert baseline_archive.read_bytes()==baseline_raw
 else:baseline_archive.parent.mkdir(parents=True,exist_ok=True);baseline_archive.write_bytes(baseline_raw)
 producer=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py';producer_ref=ref(producer)
 assert len(selection['rows'])==len(prior['rows']) and len({r['uid']for r in selection['rows']})==len(selection['rows'])
 paths=[__file__,old/'diagnostic.json.gz',old/'result.json',geometry,physical/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'test_exact_original_paired_finite_clearance_20261010.py',HERE/'original_paired_finite_chunk_accounting_20261010.py',HERE/'test_original_paired_finite_chunk_accounting_20261010.py',producer,baseline_archive]
 paths=list(map(Path,paths));refs=[ref(x)for x in paths]
 spec=importlib.util.spec_from_file_location('paired_chunk_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freeze=importlib.util.module_from_spec(spec);assert ref(producer)==producer_ref;spec.loader.exec_module(freeze);assert ref(producer)==producer_ref
 claim=reservations.claim('paired-finite-chunks-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation'];newchunks=0;results=[];chunkrefs=[];clock=time.monotonic()
 def renew():
  nonlocal clock
  assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);clock=time.monotonic()
 try:
  for row,cached in zip(selection['rows'],prior['rows']):
   assert cached['uid']==row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==cached['sourceSHA256'];tri=decode_original_world_triangles(raw)
   actual=next(r for r in runtime['rows']if r['uid']==row['uid']);world=np.asarray(actual['position'],float).reshape(-1,3)[np.asarray(actual['index']).reshape(-1,3)];ground=np.asarray(actual['drawnGroundGeometry'],float).reshape(-1,3,3)
   assert world.shape==tri.shape and len(cached['allFaces'])==len(tri)
   binding=dict(frozenCoarseCapturedGroundBaselineManifestSHA256=baseline_sha,currentMapMayHavePublishedElsewhere=True,freshCurrentAcceptance=False,freezeProducer=producer_ref,uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),inputRefs=refs+[ref(asset)],chunkFaces=a.chunk_faces)
   assert binding['completeOriginalWorldSHA256']==cached['completeOriginalWorldSHA256'] and binding['completeActualRenderedWorldSHA256']==cached['completeActualRenderedWorldSHA256'] and binding['completeGroundSHA256']==cached['completeGroundSHA256']
   final=[]
   for first in range(0,len(tri),a.chunk_faces):
    renew()
    end=min(first+a.chunk_faces,len(tri));name=a.batch+'-chunk-'+row['uid'].replace('/','-').replace(':','-')+'-'+str(first).zfill(6)+'-'+str(end).zfill(6);folder=base/name;chunkfile=folder/'face-chunk.json.gz'
    if(folder/'result.json').exists():
     cr=fenced(folder);assert ref(chunkfile)in cr['evidenceRefs'];chunk=read(chunkfile);print(json.dumps(dict(uid=row['uid'],reusedFencedFaceChunk=[first,end])),flush=True)
    else:
     assert not folder.exists(),'Incomplete chunk is not reusable; preserve and investigate separately'
     if a.max_new_chunks is not None and newchunks>=a.max_new_chunks:
      print(json.dumps(dict(resumableIncomplete=True,completedNewChunks=newchunks,sourceGeometryChanges=0,fullAcceptance=False)),flush=True);return
     faces=[]
     for i in range(first,end):
      c=cached['allFaces'][i];assert c['sourceFace']==i
      original=None if c['completeOriginal']['existingOrdinaryClearanceBoundProved']else verify(tri[i],ground)
      if c['actualRendered']['existingOrdinaryClearanceBoundProved']:rendered=None
      elif original is not None and np.array_equal(tri[i],world[i]):rendered=original
      else:rendered=verify(world[i],ground)
      faces.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=c,pairedExactOriginalFiniteBound=original,pairedExactActualRenderedFiniteBound=rendered,completeOriginalBoundProved=c['completeOriginal']['existingOrdinaryClearanceBoundProved']or bool(original and original['existingOrdinaryClearanceBoundProved']),completeActualRenderedBoundProved=c['actualRendered']['existingOrdinaryClearanceBoundProved']or bool(rendered and rendered['existingOrdinaryClearanceBoundProved'])))
      if time.monotonic()-clock>=20:
       renew();print(json.dumps(dict(uid=row['uid'],face=i,total=len(tri),chunk=[first,end])),flush=True)
     chunk=dict(binding=binding,first=first,endExclusive=end,faces=faces,fullAcceptance=False,installationApproved=False)
     verify_chunk(chunk,binding,tri,world,ground,cached['allFaces'],first,end)
     for r in binding['inputRefs']:assert ref(ROOT/r['path'])==r
     renew();assert ref(producer)==producer_ref;save(chunkfile,chunk);freeze.freeze(name,'source-bound-exact-paired-finite-face-chunk-v3',paths+[asset,chunkfile],dict(uids=[row['uid']],binding=binding,first=first,endExclusive=end,completeFaces=end-first,fullAcceptance=False));newchunks+=1
    final.extend(verify_chunk(chunk,binding,tri,world,ground,cached['allFaces'],first,end));chunkrefs.extend([ref(chunkfile),ref(folder/'result.json')])
   assert len(final)==len(tri) and [r['sourceFace']for r in final]==list(range(len(tri)))
   results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),completeOriginalWorldSHA256=binding['completeOriginalWorldSHA256'],completeActualRenderedWorldSHA256=binding['completeActualRenderedWorldSHA256'],completeGroundSHA256=binding['completeGroundSHA256'],allFaces=final,unprovedOriginalFaces=[r['sourceFace']for r in final if not r['completeOriginalBoundProved']],unprovedActualRenderedFaces=[r['sourceFace']for r in final if not r['completeActualRenderedBoundProved']]));refs.append(ref(asset));paths.append(asset)
  renew();assert ref(producer)==producer_ref
  for r in refs:assert ref(ROOT/r['path'])==r
  result=dict(frozenCoarseCapturedGroundBaselineManifestSHA256=baseline_sha,groundQualification='Frozen complete coarse captured drawn ground; source-only refinement, no fresh-current/native reacceptance even if unrelated publication changes global manifest',freshCurrentAcceptance=False,nativeReacceptance=False,rows=results,allWholeOriginalAndRenderedBoundsProved=all(not r['unprovedOriginalFaces']and not r['unprovedActualRenderedFaces']for r in results),rawPriorDiagnosticChanged=False,earlierCoarseBoundFailuresPreserved=True,pairedClippedSourceHeights=True,immutableFencedFaceChunks=True,sourceOnlyFrozenBaselineRefinement=True,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,evidenceRefs=refs+chunkrefs)
  save(doc/'diagnostic.json.gz',result);renew();assert ref(producer)==producer_ref;freeze.freeze(a.batch,'complete-original-rendered-paired-finite-resumable-v3',paths+[doc/'diagnostic.json.gz']+[ROOT/r['path']for r in chunkrefs],dict(uids=[r['uid']for r in results],completeOriginalFaces=sum(r['completeOriginalFaces']for r in results),allWholeOriginalAndRenderedBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedOriginalCounts={r['uid']:len(r['unprovedOriginalFaces'])for r in results},unprovedRenderedCounts={r['uid']:len(r['unprovedActualRenderedFaces'])for r in results},rawPriorDiagnosticChanged=False,fullAcceptance=False))
  print(json.dumps(dict(allWholeBoundsProved=result['allWholeOriginalAndRenderedBoundsProved'],unprovedOriginalCounts={r['uid']:len(r['unprovedOriginalFaces'])for r in results},unprovedRenderedCounts={r['uid']:len(r['unprovedActualRenderedFaces'])for r in results})),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
