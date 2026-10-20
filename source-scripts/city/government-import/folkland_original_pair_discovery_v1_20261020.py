"""Find exact original Folkland tower/podium candidates; no geometry or publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-original-pair-discovery-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');selection=SRC/'selection.json.gz'
 bound=next(e for e in receipt['evidenceRefs']if e['path']==str(selection.relative_to(ROOT)));assert digest(selection.read_bytes())==bound['sha256']
 tower=next(r for r in read(selection)['rows']if r['uid']=='landsd/264677:0');tile=ROOT/'3d-viewer/city/data/tiles/0_-2.json'
 forms={b['uid']:b for b in read(tile)['buildings']if b['uid']in ['landsd/264677:0','landsd/225387:0']};assert len(forms)==2
 assert forms['landsd/264677:0']['parent']==forms['landsd/225387:0']['parent']
 assert forms['landsd/264677:0']['baseHeightHKPD']==forms['landsd/225387:0']['topHeightHKPD']==12
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(tower['native']['cacheKey'],)).fetchone()
  assert sha==tower['native']['resultSha']
 hits=[]
 for model in result['models']:
  for candidate in model.get('matching',{}).get('officialCandidates',[]):
   for uid,b in forms.items():
    if candidate.get('objectId')==b['objectId'] and candidate.get('buildingCSUID')==b['buildingCSUID']:
     hits.append(dict(uid=uid,model=model,candidate=candidate,nativeStageKey=tower['native']['cacheKey'],nativeStageSHA256=sha))
 save(DOC/'registry.json.gz',dict(cacheKey=tower['native']['cacheKey'],resultSHA256=sha,result=result))
 save(DOC/'nominations.json',dict(rows=hits,sourceForms= forms,missing=sorted(set(forms)-{h['uid']for h in hits}),installationApproved=False,qualification='Exact object/CSUID nominations and matching recorded support elevations; physical, identity and runtime checks remain required.'))
 refs=[Path(__file__),SRC/'result.json',selection,tile]
 r=module('folkland_discovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-tower-podium-discovery',refs,dict(uids=sorted(forms),found=sorted({h['uid']for h in hits}),installationApproved=False))
 print(dict(jobId=r['jobId'],found=[(h['uid'],h['model']['modelId'],h['model']['triangles'])for h in hits]),flush=True)
if __name__=='__main__':main()
