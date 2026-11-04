"""Bounded whole-original distance check for Oi Sin's recorded rim failures."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'government-xl-coverage-assembly-closure-20261007-256280-0'
BATCH='government-xl-oi-sin-original-interfaces-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/256280:0';SUPPORT='landsd/91128:0'
def main():
 assert not DOC.exists()
 count=BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json'
 require_remaining(count,UID,'3c20ebb504b2dd4aab88286955d418fee94dacd76c9d7315b8e5e94dbaecc014')
 receipt=read(OLD/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[Path(__file__),count,OLD/'result.json'];pins={r['path']:r['sha256']for r in receipt['evidenceRefs']}
 for p in [OLD/'support-inputs.json',OLD/'support-checks.json.gz']:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 inputs=read(OLD/'support-inputs.json');rows=inputs['sources'];assert {r['uid']for r in rows}=={UID,SUPPORT}
 decoder=module('oi_sin_original_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL;triangles={}
 for r in rows:
  src=ROOT/r['candidate']['path'];raw=src.read_bytes();assert digest(raw)==r['sourceSHA256'];dest=LOCAL/'assets'/src.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);refs.append(src);triangles[r['uid']]=decoder.glb_triangles(r)
 row=read(OLD/'support-checks.json.gz')['rows'][0];assert row['uid']==UID and row['supportUid']==SUPPORT
 failures=row['interface']['unresolved'];out=[];support=triangles[SUPPORT]
 for f in failures:
  i,q,d=nearest(np.asarray(f['position']),support)
  out.append(dict(position=f['position'],reason=f['reason'],verticalGapM=f.get('gap'),nearestSupportFace=i,nearestPoint=q.tolist(),nearestDistanceM=d))
 summary=dict(uid=UID,supportUid=SUPPORT,completeOriginalSupportFaces=len(support),failedSamples=len(out),withinOneMillimetre=sum(r['nearestDistanceM']<=.001 for r in out),fartherThanHalfMetre=sum(r['nearestDistanceM']>.5 for r in out),maximumNearestDistanceM=max(r['nearestDistanceM']for r in out),fullAcceptance=False,qualification='All original podium faces examined for each recorded failed sample. Distances nominate further interface work only; they do not approve contact, identity, terrain, or installation.')
 save(DOC/'nearest.json.gz',dict(summary=summary,rows=out));refs.extend([HERE/'xl-second-pass.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py'])
 result=module('oi_sin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-whole-original-support-distance-v1',refs,dict(uids=[UID,SUPPORT],summary=summary,nextStep='Inspect original finite interfaces for close points and acquire missing source context for any real gaps; preserve all acceptance gates.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
