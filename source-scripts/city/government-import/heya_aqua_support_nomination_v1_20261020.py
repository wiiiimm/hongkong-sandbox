"""Nominate exact provider/installed support sources for two floating originals.

Bounds are discovery only, not physical contact or identity acceptance.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-heya-aqua-support-nomination-v1-20261020';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
UIDS=['landsd/184287:0']
def main():
 assert not DOC.exists()
 receipt=read(PRIOR/'result.json');pins={r['path']:r['sha256']for r in receipt['evidenceRefs']};sel=PRIOR/'selection.json.gz'
 assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))]
 rows=[r for r in read(sel)['rows']if r['uid']in UIDS];assert len(rows)==1
 mp=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(mp.read_bytes());manifest=read(mp)
 refs=[Path(__file__),PRIOR/'result.json',sel,mp];installed=[];catalogueHashes={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogueHashes[p]=digest(p.read_bytes());refs.append(p)
  for e in read(p)['models']:installed.append((e,p))
 assert not set(UIDS)&{e['uid']for e,p in installed}
 out=[]
 def overlaps(a,b):return a[0][0]<=b[1][0] and b[0][0]<=a[1][0] and a[0][2]<=b[1][2] and b[0][2]<=a[1][2]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in rows:
   key=r['native']['cacheKey'];sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==r['native']['resultSha']
   bounds=r['candidate']['entry']['worldBounds'];candidates=[]
   for m in native['models']:
    if m['modelId']==r['modelId']:continue
    b=m.get('worldBounds')
    if b and overlaps(bounds,b) and b[0][1]<=bounds[0][1]+.001 and b[1][1]>=bounds[0][1]-.001:
     candidates.append(dict(origin='same-provider-stage',modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],worldBounds=b,officialCandidates=m.get('matching',{}).get('officialCandidates',[])))
   for e,p in installed:
    b=e['worldBounds']
    if overlaps(bounds,b) and b[0][1]<=bounds[0][1]+.001 and b[1][1]>=bounds[0][1]-.001:
     asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];refs.extend([p,asset]);candidates.append(dict(origin='installed-catalogue',uid=e['uid'],modelId=e.get('modelId'),sourceSHA256=e['sha256'],triangles=e['triangles'],worldBounds=b,catalogue=str(p.relative_to(ROOT))))
   out.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],worldBounds=bounds,nativeStageKey=key,nativeStageSHA256=sha,candidates=candidates));print({'uid':r['uid'],'nominations':[(x.get('uid') or x['modelId'],x['origin'])for x in candidates]},flush=True)
 assert digest(mp.read_bytes())==mh
 for p,h in catalogueHashes.items():assert digest(p.read_bytes())==h
 save(DOC/'nominations.json',dict(rows=out,currentManifestSHA256=mh,scope='Same exact provider stage and all current installed native catalogue bounds only; no claim that other provider tiles contain no support.',boundsOnly=True,physicalContactVerified=False,identityApproved=False,installationApproved=False,sourceGeometryChanges=0))
 module('two_tower_nomination_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-support-source-discovery',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=out,installationApproved=False))
if __name__=='__main__':main()
