"""Verify shared procedural correction against collision-checked exact generated geometry."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-villa-canopy-shared-integration-v1-20261015'
def main():
 assert not DOC.exists();DOC.mkdir();testpaths=['3d-viewer/city/tests/procedural-footprint-corrections.test.js','3d-viewer/city/tests/building-geometry.test.js'];result=subprocess.run(['node','--test',*testpaths],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(DOC/'tests.log').write_text(result.stdout);assert result.returncode==0
 capture=B/'government-xl-villa-private-canopy-collision-v2-20261015/rendered.json';receipt=read(capture.parent/'result.json');pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']};assert digest(capture.read_bytes())==pins[str(capture.relative_to(ROOT))]
 p=B/'government-xl-villa-private-canopy-quantised-boundary-v2-20261015/proposal.json';plan=read(p);assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==plan['manifestSHA256'];assert digest((ROOT/'3d-viewer/city/data/tiles/-7_-9.json').read_bytes())==plan['tileSHA256']
 out={'uids':[plan['uid'],plan['sourceBuildingUID']],'testExitCode':result.returncode,'productionMeshExactlyMatchesCollisionCheckedCandidate':True,'officialFormUnchanged':True,'sourceBuildingGeometryChanged':False,'runtimeProceduralCodeChanged':True,'fullAcceptance':False,'installed':False,'nextStep':'Refresh complete five-source placed runtime, foundation, terrain and affected neighbour scope against current snapshot; run browser checks before original-model publication. Existing historical physical worker pins an older manifest and must not be rerun unchanged.'};save(DOC/'summary.json',out)
 paths=[Path(__file__),capture,capture.parent/'result.json',p]+[ROOT/x for x in testpaths+['3d-viewer/city/building-geometry.js','3d-viewer/city/procedural-footprint-corrections.js','3d-viewer/city/tai-o-estimates.js','3d-viewer/vendor/three.module.js','3d-viewer/vendor/BufferGeometryUtils.js','3d-viewer/city/data/manifest.json','3d-viewer/city/data/tiles/-7_-9.json']]
 module('villa_shared_integration_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'source-bound-shared-procedural-render-collision-integration-v1',paths,out)
if __name__=='__main__':main()
