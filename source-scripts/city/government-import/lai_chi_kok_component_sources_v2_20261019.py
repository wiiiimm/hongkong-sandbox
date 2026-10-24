"""Locate exact government rooftop counterparts; diagnostic only, no publication."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lai-chi-kok-component-sources-v2-20261019'
DOC=BASE/BATCH
PRIOR=BASE/'government-xl-next-five-original-identity-v1-20261018'
def main():
 assert not DOC.exists()
 prior=BASE/'government-xl-lai-chi-kok-neighbour-projection-v1-20261019'
 receipt=read(prior/'result.json');refs=[Path(__file__),prior/'result.json'];models=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 wanted={r['uid']for r in read(prior/'projection.json')['rows']};assert len(wanted)==7
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  matches=c.execute("SELECT r.cache_key,r.result_sha,i.sheet,m FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result::jsonb->'models') m WHERE m->'candidate'->>'uid'=ANY(%s)",(sorted(wanted),)).fetchall()
  bindings={}
  for cache_key,result_sha,sheet,m in matches:
   uid=m['candidate']['uid']; asset=m['asset']['sha256']; token=(uid,asset)
   if token not in bindings:
    models.append(m);bindings[token]=dict(cacheKey=cache_key,resultSha=result_sha,sheet=sheet,model=m)
 paths=subprocess.check_output(['/home/williamli/.codex/packages/app-server-daemon/releases/0.163.0-x86_64-unknown-linux-musl/codex-path/rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines()
 hashes={m['asset']['sha256'] for m in models};cached={}
 for name in paths:
  p=ROOT/name;h=p.name.removesuffix('.glb.gz')
  if h in hashes and h not in cached and digest(p.read_bytes())==h:cached[h]=name;refs.append(p)
 rows=[dict(uid=m['candidate']['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],cachePath=cached.get(m['asset']['sha256']),native=bindings[(m['candidate']['uid'],m['asset']['sha256'])])for m in models]
 missing=sorted(wanted-{r['uid']for r in rows})
 save(DOC/'sources.json.gz',dict(rows=rows,missingFromTerminalStage=missing,installationApproved=False))
 summary=dict(uids=sorted(wanted),matched=len(rows),cached=sum(bool(r['cachePath'])for r in rows),missingFromTerminalStage=missing,installationApproved=False)
 print(summary,flush=True)
 module('kai_component_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-original-rooftop-counterpart-discovery',refs,summary)
if __name__=='__main__':main()
