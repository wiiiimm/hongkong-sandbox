"""Preserve an intentionally stopped camera-mismatch diagnostic, never acceptance."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-elegant-garden-focused-post-mobile-views-v1-20261028'

def main():
 out=BASE/BATCH;assert out.exists()and not(out/'result.json').exists()
 tool=HERE/'private_viewer_runtime_closure_v1_20261028.mjs'
 subprocess.run(['node',str(tool),'verify',str((out/'runtime-input-closure.json').relative_to(ROOT))],cwd=ROOT,check=True)
 report=dict(uids=['landsd/99061:0','landsd/336456:0'],status='intentionally-aborted-known-diagnostic-camera-mismatch',diagnosticOnly=True,visualReviewApproved=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,publication=False,supervisedRunnerExitCode=130,supervisedRunnerReleased=True,
  reason='The first nominated camera distance2.527m is below the unchanged production OrbitControls minimum12m; elevation0.05also exceeds its near-horizontal polar limit. controls.update clamps the capture away from the nominated safe raycast position. ROOT inspected the first2exports and found them unsuitable. No rendered camera position was recorded, so nominal ray counts cannot qualify appearance.',
  qualification='Known test bug, not source corruption or model rejection. The exact supervised runner was cancelled through its existing signal handler; its process group stopped and reservation release returned true. The private server closed with that worker. No full browser report or success is inferred from the preserved partial exports. V2uses an explicitly labelled private free-camera observation and verifies its synchronous rendered position; it does not change production orbit constraints or claim normal-orbit accessibility.')
 save(out/'aborted-diagnostic.json',report)
 refs=[Path(__file__),HERE/'elegant_focused_post_views_v1_20261028.py',HERE/'elegant_focused_post_views_v1_20261028.mjs',ROOT/'3d-viewer/city/app.js',tool]
 for p in read(out/'runtime-input-closure.json')['inputHashes']:refs.append(ROOT/p)
 module('focused_post_abort_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aborted-private-post-camera-diagnostic-with-known-orbit-clamp-mismatch',refs,report)

if __name__=='__main__':main()
