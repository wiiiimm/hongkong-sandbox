"""Locate exact government rooftop counterparts; diagnostic only, no publication."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-kai-tak-cruise-component-sources-v1-20261019'
DOC=BASE/BATCH
PRIOR=BASE/'government-xl-next-five-original-identity-v1-20261018'
def main():
 assert not DOC.exists()
 context=read(PRIOR/'263423:0/context.json')
 wanted={r['uid'] for r in context['identity']['intersectingForms'] if r['uid']!='landsd/263423:0'}
 row=next(r for r in read(PRIOR/'selection.json.gz')['rows'] if r['uid']=='landsd/263423:0')
 key=row['native']['cacheKey'];refs=[Path(__file__),PRIOR/'selection.json.gz',PRIOR/'263423:0/context.json'];models=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()
  assert sha==row['native']['resultSha']
  sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0]
  for m in result['models']:
   if m.get('candidate',{}).get('uid') in wanted:models.append(m)
 paths=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines()
 hashes={m['asset']['sha256'] for m in models};cached={}
 for name in paths:
  p=ROOT/name;h=p.name.removesuffix('.glb.gz')
  if h in hashes and h not in cached and digest(p.read_bytes())==h:cached[h]=name;refs.append(p)
 rows=[dict(uid=m['candidate']['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],cachePath=cached.get(m['asset']['sha256']),native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m))for m in models]
 missing=sorted(wanted-{r['uid']for r in rows})
 save(DOC/'sources.json.gz',dict(rows=rows,missingFromTerminalStage=missing,installationApproved=False))
 summary=dict(uids=sorted(wanted),matched=len(rows),cached=sum(bool(r['cachePath'])for r in rows),missingFromTerminalStage=missing,installationApproved=False)
 print(summary,flush=True)
 module('kai_component_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-original-rooftop-counterpart-discovery',refs,summary)
if __name__=='__main__':main()
