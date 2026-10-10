"""Freeze exact typed embedded references; no numeric exclusions or model acceptance."""
import importlib.util,json,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
import lippo_exact_pending_embedded_geometry_reference_v1_20261011 as typed
BATCH='government-xl-lippo-pending-typed-embedded-source-reference-diagnostic-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
AUDIT=Path('/tmp/xl-lippo-exact-pending-additive-resume-root-closure-20261011.log')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 capture=ROOT/typed.CAPTURE_PATH;tile=ROOT/typed.TILE_PATH
 before=capture.read_bytes();tile_raw=tile.read_bytes();resolver=typed.BoundResolver(before,tile_raw)
 proofs=[resolver.resolve(typed.CAPTURE_PATH,p,typed.at(resolver.context,p)) for p in typed.POINTERS]
 assets=[]
 for uid in typed.ACTORS:
  actors=[b for b in resolver.tile['buildings'] if b.get('uid')==uid];assert len(actors)==1
  raw=typed.canonical(actors[0]['modelGeometry']);csuid,model,pin,nbytes=typed.ACTORS[uid]
  assert digest(raw)==pin and len(raw)==nbytes
  p=DOC/(uid.split('/')[1].replace(':','-')+'-complete-canonical-embedded-geometry.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);assets.append(ref(p))
 assert AUDIT.is_file();p=DOC/'preserved-ordinary-v5-typed-reference-mismatch.log';p.write_bytes(AUDIT.read_bytes())
 diagnostic=dict(batch=BATCH,capture=ref(capture),completeCurrentTile=ref(tile),typedReferences=proofs,
  completeCanonicalGeometryAssets=assets,ordinaryV5MismatchLog=ref(p),
  numericGeometryExcluded=False,metadataBoundarySkipped=False,ordinaryFileSHAOutsideExactPointersUnchanged=True,
  identityAccepted=False,physicalAccepted=False,installationApproved=False,publication=False,newlyInstalled=0,
  qualification='Original sourceEvidence explicitly identifies canonical embedded modelGeometry JSON SHA, not the whole containing tile. Six exact immutable document pointers are positively verified against complete unique current actor geometry; no source or current physical acceptance is conferred.')
 save(DOC/'diagnostic.json.gz',diagnostic)
 test=HERE/'test_lippo_exact_pending_embedded_geometry_reference_v1_20261011.py'
 proc=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p',test.name,'-v'],cwd=ROOT,capture_output=True,text=True)
 save(DOC/'tests.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,actualSourceCounterexamples=True));assert proc.returncode==0,proc.stderr
 assert capture.read_bytes()==before and tile.read_bytes()==tile_raw
 refs=[Path(__file__),HERE/'lippo_exact_pending_embedded_geometry_reference_v1_20261011.py',test,capture,tile,
  HERE/'verify_lippo_closed_model_checkpoint_typed_embedded_v6_20261011.py']
 spec=importlib.util.spec_from_file_location('lippo_typed_reference_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'six-exact-pending-routing-embedded-geometry-source-references-no-exclusions',refs,
  dict(uids=sorted(typed.ACTORS),typedReferenceCount=6,completeEmbeddedGeometryActors=3,numericGeometryExcluded=False,
  metadataBoundarySkipped=False,ordinaryFileSHAOutsideExactPointersUnchanged=True,identityAccepted=False,
  physicalAccepted=False,installationApproved=False,publication=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=result['jobId'],typedReferenceCount=6,numericGeometryExcluded=False,publication=False)),flush=True)
if __name__=='__main__':main()
