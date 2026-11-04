"""Capture production terrain with the validated private HKUST patch, no publication."""
from pathlib import Path
import subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-private-overlap-proof-v1-20261015';CURRENT=B/'government-xl-hkust-pair-current-ground-v1-20261015';DOC=B/'government-xl-hkust-private-runtime-capture-v1-20261015';JS=HERE/'hkust_private_ground_capture_v1_20261015.mjs'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();r=read(OLD/'result.json');assert r['validatorPassed'];patch=OLD/'private-native-patch.json';assert ref(patch) in r['evidenceRefs'];plan=read(CURRENT/'plan.json');source=ROOT/plan['sourceInput']['path'];assert ref(source)==plan['sourceInput'];parentplan=read(B/'government-xl-hkust-private-native-candidate-v2-20261015/proposal.json');mp=ROOT/'3d-viewer/city/data/manifest.json';assert ref(mp)==parentplan['manifest'];claim=reservations.claim('hkust-private-runtime-'+str(uuid.uuid4()),['private-runtime:'+DOC.name],batch=DOC.name,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();paths=[Path(__file__),JS,OLD/'result.json',patch,CURRENT/'plan.json',source];plan.update(privateTerrain=ref(patch),expectedManifest=ref(mp)['sha256'],evidenceRefs=[ref(p) for p in paths]);save(DOC/'plan.json',plan)
  with (DOC/'capture.log').open('w') as log:subprocess.run(['node',str(JS),str((DOC/'plan.json').relative_to(ROOT)),str((DOC/'ground.json.gz').relative_to(ROOT))],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
  g=read(DOC/'ground.json.gz');samples=g['originalRimGroundSamples'];gaps=[x['currentTerrainGap'] for x in samples];summary={'uids':r['uids'],'rimSamples':len(samples),'belowHalfMetreSamples':sum(x<-.5 for x in gaps),'abovePointOneMetreSamples':sum(x>.1 for x in gaps),'withinPointOneMetreSamples':sum(abs(x)<=.1 for x in gaps),'minimumGapM':min(gaps),'maximumGapM':max(gaps),'completeDrawnGroundFaces':g['completeTraversedDrawnGroundFaces'],'regionalGroundFaces':g['completeRegionalGroundFaces'],'privateTerrainGeometryChanged':True,'liveTerrainGeometryChanged':False,'sourceBuildingGeometryChanged':False,'fullAcceptance':False,'providerOriginalPointContextOnly':True};save(DOC/'summary.json',summary)
  for p,h in g['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
  module('hkust_private_runtime_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-production-private-terrain-capture-v1',paths,{**summary,'nextStep':'Compare whole sources/actual model placement and current neighbours over complete parent extent; retain source-wall and identity findings. This private point capture is not acceptance.'});print(summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
