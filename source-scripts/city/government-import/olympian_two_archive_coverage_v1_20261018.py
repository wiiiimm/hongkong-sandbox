"""Record bounded original archive/index coverage and independently verify new diagnostics."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-archive-coverage-v1-20261018';DOC=BASE/BATCH
NAMES=['canonical-contacts-v1','spatial-support-lookup-v2','nearest-interfaces-v1','tower1-local-paths-v1']
def main():
 assert not DOC.exists();refs=[Path(__file__)];verified=[];rows=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/('government-xl-olympian-two-'+name+'-20261018')/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);pins={}
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
   for q,h in pins.items():assert digest((ROOT/q).read_bytes())==h,q
   verified.append(dict(batch=r['batch'],jobId=r['jobId'],exactNeonResult=True,verifiedDistinctRefs=len(pins)));refs.extend([p,*[ROOT/q for q in pins]])
  records=c.execute("SELECT i.cache_key,i.sheet,r.result_sha,m.value->>'modelId' FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m WHERE i.stage='native-prepare' AND i.sheet IN ('11-NW-19A','11-NW-19C')").fetchall();ids={x[3]for x in records}
 recovery=BASE/'government-xl-olympian-two-source-local-terrain-20261008/source-recovery.json';refs.append(recovery)
 for sheet in read(recovery)['sheets']:
  p=ROOT/sheet['cache']/'directory/result.json';d=read(p);refs.append(p);near=[]
  for m in d['models']:
   g=m['geoRefNo'];x=int(g[:5])-34500;z=16500-int(g[5:])
   if 0<=x<=600 and -3550<=z<=-2900:near.append(dict(modelId=m['modelId'],subtype=m['subtype'],indexed=m['modelId']in ids,approxGeoRefPosition=[x,z]))
  rows.append(dict(sheet=sheet['sheet'],directorySHA256=d['directorySHA256'],models=near,unindexed=[m['modelId']for m in near if not m['indexed']]))
 save(DOC/'archive-index-coverage.json',dict(rows=rows,indexedRecords=[list(x)for x in records],qualification='Frozen local official archive directories, bounded GeoRef anchor window only. Not an exhaustive whole-government spatial exclusion or live source revision check.'))
 save(DOC/'ROOT-VERIFIED.json',dict(stages=verified))
 (DOC/'HANDOFF.md').write_text('Olympian original recovery remains unfinished; no installation or permanent rejection.\n\nCanonical full edge+vertex samples preserve 2/625/696/630 unresolved positions for towers 1/2/3/5. All-indexed-sheet bounds search nominated no further support. All 116 archive model anchors in the bounded local window are indexed. The additional original podium239351 did not clear the interfaces.\n\nComplete nearest-triangle checks: Tower1 two points are within0.013668m, but neither has a finite original intersection within the existing0.5m local path test. Do not report proximity as contact. Towers2/3/5 maximum distances are5.09005/5.04876/4.87544m; source-specific underside/overhang interpretation requires additional evidence. Tower1 failures are narrow nearly vertical original faces724/725/3756 extending below26.63m; no geometry edit is authorised or made.\n\nNext: inspect full source lower-face roles and primary architect/developer evidence before any bounded original-interface interpretation, then actual renderer four-coordinate-mode and complete foundation checks. Separate original265851 terrain low-rim1.130128m and four current BASIC-neighbour regressions still need resolution; do not replay the failed root-ground retention. No acceptance limits changed. Full XL status remains260installed/261remaining of521.\n')
 out=module('olympian_archive_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-bounded-archive-index-coverage-and-recovery-handoff-v1',list(set(refs)),dict(uids=['landsd/265851:0','landsd/270317:0','landsd/269908:0','landsd/269839:0','landsd/269837:0'],fullAcceptance=False,newlyInstalled=0,currentHeldReason='original-assembly-support-interpretation-and-terrain-neighbour-failures',nextStep='Primary source/component review, then actual four-world full acceptance; no repeat unchanged archive or proximity checks.'));print(dict(jobId=out['jobId'],verified=verified),flush=True)
if __name__=='__main__':main()
