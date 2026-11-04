"""Read-only original source lookup for adjoining Park Avenue assembly actors."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-base-neighbour-lookup-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);tile=ROOT/'3d-viewer/city/data/tiles/0_-2.json';wanted={'landsd/80093:0','landsd/81847:0','landsd/82015:0'};forms=[b for b in read(tile)['buildings']if b['uid']in wanted];assert len(forms)==3;prefixes={}
 for b in forms:prefixes.setdefault(b['buildingCSUID'][:10],[]).append(b['uid']);rows=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for cache,sheet,resultsha,m in c.execute("SELECT i.cache_key,i.sheet,r.result_sha,m.value FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m WHERE i.stage='native-prepare' AND EXISTS (SELECT 1 FROM unnest(%s::text[]) p WHERE strpos(m.value->>'modelId',p)>0)",(list(prefixes),)).fetchall():
   match=[uid for prefix,uids in prefixes.items()if prefix in m.get('modelId','') for uid in uids]
   assert match;rows.append(dict(cacheKey=cache,sheet=sheet,resultSHA256=resultsha,matchedUids=match,model=m))
 save(DOC/'matches.json',dict(sheet='all existing indexed sheets',forms=forms,matches=rows,fullAcceptance=False,qualification='Exact CSUID numeric prefix nomination only; not source identity or placement approval. Search covers existing native-prepare results across all indexed sheets.'))
 summary=[dict(uid=u,modelId=r['model'].get('modelId'),cacheKey=r['cacheKey'],state=r['model'].get('state'),asset=r['model'].get('asset'),candidateUid=r['model'].get('candidate',{}).get('uid'))for r in rows for u in r['matchedUids']];save(DOC/'summary.json',dict(rows=summary,manifestSHA256=digest(manifestpath.read_bytes()),newlyInstalled=0));out=module('olympian_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-adjoining-park-avenue-original-component-lookup-v1',[Path(__file__),tile,manifestpath],dict(uids=sorted(wanted),matchedEntries=len(rows),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],rows=summary),flush=True)
if __name__=='__main__':main()
