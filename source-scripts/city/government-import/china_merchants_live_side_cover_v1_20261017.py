"""Current drawn terrain plus immutable source, scoped side-exposure diagnostic."""
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from china_merchants_directional_cover_v1_20261017 import inspect_direction
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-live-side-cover-v1-20261017';DOC=BASE/BATCH
CAP=BASE/'government-xl-china-merchants-live-baseline-foundation-v1-20261017'
RT=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
OLD=BASE/'government-xl-china-merchants-directional-cover-v1-20261017'
SOURCE=BASE/'government-xl-china-merchants264206-saved-face-attribution-v1-20261013/source-face-attribution.json.gz'
def main():
 assert not DOC.exists();saved=read(SOURCE);require_remaining(BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json',saved['uid'],saved['sourceSHA256'])
 refs=[Path(__file__),RT,SOURCE,CAP/'result.json',OLD/'result.json',OLD/'directional-cover.json.gz',HERE/'china_merchants_directional_cover_v1_20261017.py',HERE/'china_merchants_upward_source_cover_v1_20261015.py']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for doc in [CAP,OLD]:
   r=read(doc/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 capture=read(RT)
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 g=capture['rows'][0];assert g['sourceSHA256']==saved['sourceSHA256'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];original=np.asarray(saved['completeOriginalSourceFaceVerticesInOrdinalOrder']);assert t.shape==original.shape==(19551,3,3);delta=float(np.max(np.abs(t-original)));assert delta<1e-10
 ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);both=np.concatenate([t,ground]);old=read(OLD/'directional-cover.json.gz');ids=sorted({r['sourceFace'] for a in old['rows'] if a['axis']!=1 for r in a['faces'] if r['uncoveredAreaM2']>1e-8});assert len(ids)==39
 rows=[];summary=[]
 for axis in [0,2]:
  for sign in [-1,1]:
   found=inspect_direction(both,ids,axis,sign);rows.append(dict(axis=axis,sign=sign,faces=found));summary.append(dict(axis=axis,sign=sign,uncoveredFaces=[r['sourceFace'] for r in found if r['uncoveredAreaM2']>1e-8],uncoveredProjectedAreaM2=sum(r['uncoveredAreaM2'] for r in found)));print(summary[-1],flush=True)
 save(DOC/'live-side-cover.json.gz',dict(uid=saved['uid'],sourceSHA256=saved['sourceSHA256'],originalFaces=len(t),drawnTerrainFaces=len(ground),sourceCoordinateMaximumDeltaM=delta,selectedFaces=ids,rows=rows,summary=summary,qualification='Only the 39 previously source-side-exposed faces; not the entire current 598-face foundation failure set. Occluder ordinals >=19551 are drawn terrain faces. Four horizontal directions, 0.01 m separation. Does not certify arbitrary camera occlusion, underground roles or acceptance.',installationApproved=False))
 out=module('china_live_side_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-drawn-terrain-original-side-cover-diagnostic-v1',refs,dict(uids=[saved['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0,nextStep='Retain current 598-face foundation hold; interpret remaining exact side-exposed source faces and separately account for newly changed failure set before any acceptance.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
