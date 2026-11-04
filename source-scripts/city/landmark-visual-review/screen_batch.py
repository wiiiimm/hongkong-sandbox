"""Classify the existing 25-model cache using shared CPU checks and explicit prior holds.
No network, inventory updates, source edits or publication. Terrain flags need context.
"""
import hashlib,json,pathlib,time,collections
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/astra-city/landmark-visual-review'
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 start=time.perf_counter()
 validation='docs/astra-city/landmark-visual-review/hks211-validation.json'
 catalogue='source-scripts/city/landmark-bulk/compact/catalogue.json'
 oldAcceptance='source-scripts/city/architecture-batch/acceptance.json'
 v=read(validation);c=read(catalogue);holds=read(oldAcceptance)['held']
 holds['landsd/211847:0']='Po Lin Hua Yan Pagoda: native geometry is at least 3.23 m above source terrain; no supporting neighbour identified in the prior landmark pass.'
 assert v['models']==v['checksPassed']==v['loaderAccepted']==25 and v['exceptions']==0
 results={r['uid']:r for r in v['results']};assert set(results)=={m['uid'] for m in c['models']}
 hashes={**v['hashes'],validation:sha(validation),catalogue:sha(catalogue),oldAcceptance:sha(oldAcceptance)}
 for path,digest in hashes.items():assert sha(path)==digest,'Inputs changed: '+path
 rows=[]
 for m in c['models']:
  uid=m['uid'];r=results[uid];asset=str(pathlib.Path(catalogue).parent/m['asset']);assert sha(asset)==m['sha256'] and (ROOT/asset).stat().st_size==m['bytes']
  if uid in holds:outcome='held-existing-placement-exception';reason=holds[uid];action='Retain fallback; higher-effort source/retaining-edge review. Do not publish automatically.'
  elif not r['concerns']:outcome='ready-for-browser-review';reason='No sampled terrain flags; runtime/source-surface checks pass.';action='Run normal-scene and foundation browser acceptance before publication.'
  else:outcome='needs-assembly-or-foundation-context';reason='CPU flags alone cannot distinguish supported tower/podium components from genuine terrain problems.';action='Review source supporting parts and normal-scene foundations together; preserve source elevations.'
  rows.append({'uid':uid,'label':m.get('label'),'modelId':m['modelId'],'sourceTile':m['sourceTile'],'sourceTileRevision':m.get('sourceTileRevision'),'asset':asset,'sha256':m['sha256'],'bytes':m['bytes'],'worldBounds':m['worldBounds'],'outcome':outcome,'reason':reason,'nextAction':action,'cpuConcerns':r['concerns'],'terrain':r['terrain']})
 report={'issue':'HKS-211','staged':True,'published':False,'verticalScale':1,'models':25,'counts':dict(collections.Counter(r['outcome'] for r in rows)),'rows':rows,'inputHashes':hashes,'cpuSeconds':v['seconds'],'classificationSeconds':time.perf_counter()-start,'networkRequests':0,'downloadedBytes':0,'aiCallsInScripts':0,'compressedBytes':sum(m['bytes']for m in c['models']),'limits':['CPU flags are not architecture acceptance or rejection.','No source geometry, terrain, live catalogue or shared inventory was changed.','Building parts are not whole-landmark completion. Existing holds are retained.']}
 (OUT/'hks211-screening.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts']))
if __name__=='__main__':main()
