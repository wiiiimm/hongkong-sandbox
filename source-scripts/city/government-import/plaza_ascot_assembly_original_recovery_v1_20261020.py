"""Recover exact nine government assets for eight related viewer identities."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-assembly-original-recovery-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-plaza-ascot-component-census-v1-20261020';GROUND=BASE/'government-xl-next-three-adjoining-ground-v1-20261020'
def main():
 assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__),HERE/'xl-second-pass.py'];receipts={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for f in [SRC,GROUND]:
   r=read(f/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f/'result.json');receipts[f]={e['path']:e['sha256']for e in r['evidenceRefs']}
  p=SRC/'census.json';assert digest(p.read_bytes())==receipts[SRC][str(p.relative_to(ROOT))];nominations=read(p);refs.append(p)
  p=SRC/'registry.json.gz';assert digest(p.read_bytes())==receipts[SRC][str(p.relative_to(ROOT))];record=read(p);refs.append(p);key=record['cacheKey'];sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==record['resultSHA256']and result==record['result'];sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0]
 rows=[]
 for n in nominations['nominations']:
  assert len(n['exactViewerUids'])==1;m=n['model'];rows.append(dict(uid=n['exactViewerUids'][0],modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m)))
 assert len(rows)==19 and len({r['uid'] for r in rows})==19
 priorpath=HERE/'local'/GROUND.name/'sheets'/sheet/'directory/result.json';assert digest(priorpath.read_bytes())==receipts[GROUND][str(priorpath.relative_to(ROOT))];refs.append(priorpath)
 cache={}
 for r in rows:
  p=HERE/'local/government-xl-next-twenty-current-terrain-v2-20261020/assets'/(r['sourceSHA256']+'.glb.gz')
  if not p.exists():p=HERE/'local/government-xl-plaza-ascot-adjacent-original-recovery-v1-20261020/assets'/(r['sourceSHA256']+'.glb.gz')
  if p.exists():assert digest(p.read_bytes())==r['sourceSHA256'];cache[r['sourceSHA256']]=p;refs.append(p)
 helper=module('mount_sterling_nine_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;recovered=helper.source_sheet(sheet,rows,read(priorpath),cache,[])
 for r in rows:
  p=LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz');assert digest(p.read_bytes())==r['sourceSHA256'];r['assetPath']=str(p.relative_to(ROOT))
 save(DOC/'recovery.json',dict(rows=rows,recovery=recovered,installationApproved=False));refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 module('mount_sterling_nine_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-nineteen-assembly-original-cache-recovery',list(dict.fromkeys(refs)),dict(uids=sorted({r['uid']for r in rows}),exactHashMatched=True,originalAssets=19,sourceGeometryChanges=0,installationApproved=False));print('Nineteen original assets recovered with exact existing SHA matches',flush=True)
if __name__=='__main__':main()
