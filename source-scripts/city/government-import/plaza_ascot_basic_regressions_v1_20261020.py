"""Locate introduced BASIC burial against terrain separately from original podium."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import'; BATCH='government-xl-plaza-ascot-basic-regressions-v1-20261020';DOC=BASE/BATCH
BEFORE=BASE/'government-xl-plaza-ascot-basic-before-v1-20261020';AFTER=BASE/'government-xl-plaza-ascot-basic-ground-v2-20261020';BASIC=BASE/'government-xl-plaza-ascot-basic-support-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'china_ferry_current_foundations_v1_20261020.py',HERE/'xl-final-script-pass.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [BEFORE,AFTER,BASIC]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 before=take(BEFORE,BEFORE/'ground.json.gz');after=take(AFTER,AFTER/'ground.json.gz');podium=np.asarray(take(BASIC,BASIC/'input.json.gz')['podium']);prior={r['uid']:r for r in before['rows']};final=module('ascot_face_regressions',HERE/'xl-final-script-pass.py');summary=[]
 for r in after['rows']:
  old=prior[r['uid']];assert old['position']==r['position'] and old['index']==r['index'];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];g=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);bg=np.asarray(old['drawnGroundGeometry']).reshape(-1,3,3)
  proofs={k:face_diagnostics(final,t,ground) for k,ground in [('before',bg),('terrainOnly',g),('terrainAndPodium',np.concatenate([g,podium]))]};sets={k:{f['faceIndex'] for f in p['buriedFaces']} for k,p in proofs.items()};new=sets['terrainAndPodium']-sets['before'];terrainnew=new&sets['terrainOnly'];podiumnew=new-sets['terrainOnly'];save(DOC/(r['uid'].split('/')[1]+'.json.gz'),dict(proofs=proofs,introducedTerrainFaces=sorted(terrainnew),introducedPodiumFaces=sorted(podiumnew),installationApproved=False));item=dict(uid=r['uid'],introducedTerrainFaces=len(terrainnew),introducedPodiumFaces=len(podiumnew),resolvedBuriedFaces=len(sets['before']-sets['terrainAndPodium']),introducedUpwardFaces=sum(f['upward'] for f in proofs['terrainAndPodium']['buriedFaces'] if f['faceIndex'] in new));summary.append(item);print(item,flush=True)
 for capture in [before,after]:
  for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=[r['uid'] for r in summary],rows=summary,installationApproved=False,sourceGeometryChanges=0,productionTerrainChanges=0);save(DOC/'summary.json',result);module('ascot_basic_regressions_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-face-before-after-terrain-versus-podium-regressions',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
