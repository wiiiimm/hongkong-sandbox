"""Refresh all basic forms in Ocean Terminal's whole changed child domain."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-current-neighbours-v1-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018';SCOPE=BASE/'government-xl-ocean-terminal-current-scope-v1-20261019'
def main():
 assert not DOC.exists();r=read(SCOPE/'result.json');refs=[Path(__file__),SCOPE/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 scope=read(SCOPE/'scope.json');assert scope['touchingNativeUids']==[] and scope['allCurrentActorsNominated'];patches=read(CAP/'terrain-candidates.json');assert len(patches)==1
 patch=patches[0];assert digest((ROOT/patch['path']).read_bytes())==patch['sha256'];parent=ROOT/'3d-viewer'/patch['replaces']['url'];assert digest(parent.read_bytes())==patch['replaces']['sha256']
 final=module('ocean_current_neighbour_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(scope['changedParentExtent']);inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms}
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=False)for b,_,_ in forms],patches=patches,candidateIds=['landsd/205767:0'],inputHashes=inputs))
 subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 report=read(DOC/'neighbour-checks.json');summary=dict(uids=['landsd/205767:0'],currentNativeActors=scope['currentNativeActors'],touchingNativeUids=[],currentBasicForms=len(forms),flagged=[dict(uid=x['uid'],reasons=x['reasons'])for x in report['rows']if x['reasons']],installationApproved=False);save(DOC/'summary.json',summary)
 for p,h in {**pins,**report['inputHashes'],**inputs}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([CAP/'terrain-candidates.json',ROOT/patch['path'],parent,HERE/'check-neighbours.mjs',HERE/'xl-final-script-pass.py'])
 module('ocean_current_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-current-whole-domain-neighbours',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
if __name__=='__main__':main()
