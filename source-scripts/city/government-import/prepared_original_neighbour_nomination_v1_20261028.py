"""Nominate nearby original units from a pinned prepared government sheet.

Metadata bounds only. No asset processing, support/identity/installation approval,
new production queue or terrain change. Preserve null candidate UIDs.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--uid',required=True);p.add_argument('--lease',required=True);p.add_argument('--inventory',default='government-xl-after-ocean-four-unfinished-exact-source-inventory-v1-20261027');p.add_argument('--padding',type=float,default=2);a=p.parse_args();assert 0<=a.padding<=10 and a.batch.startswith('government-xl-')and '/'not in a.batch
 lease=read(Path(a.lease));assert reservations.owns(lease)and 'building:'+a.uid in lease['resources'];base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
 _,pins=authenticate(base/a.inventory);source_path=base/a.inventory/'summary.json';assert digest(source_path.read_bytes())==pins[str(source_path.relative_to(ROOT))]
 row=next(r for r in read(source_path)['rows']if r['uid']==a.uid);key,model_id=row['sourceKey'].split('/',1)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert record and record[0]==row['nativeResultSHA256'];models=record[1]['models'];target=next(m for m in models if m['modelId']==model_id);lo,hi=target['worldBounds']
 candidates=[]
 for m in models:
  bounds=m.get('worldBounds')
  if m['modelId']==model_id or not isinstance(bounds,list)or len(bounds)!=2:continue
  low,high=bounds
  if not all(low[i]<=hi[i]+a.padding and high[i]>=lo[i]-a.padding for i in [0,2]):continue
  candidate=m.get('candidate')or {};candidates.append(dict(model=m,candidateUid=candidate.get('uid'),maximumYMinusTargetMinimumY=high[1]-lo[1],minimumYMinusTargetMinimumY=low[1]-lo[1],supportApproved=False,identityApproved=False))
 candidates.sort(key=lambda r:r['model']['modelId'])
 result=dict(uids=[a.uid],uid=a.uid,sourceKey=row['sourceKey'],indexedSourceSHA256=row['indexedSourceSHA256'],nativeResultSHA256=record[0],targetModel=target,paddingM=a.padding,completePreparedSheetModelCount=len(models),nearbyOriginalCandidates=candidates,candidates=len(candidates),lowerOriginalCandidates=sum(r['model']['worldBounds'][0][1]<=lo[1]+1 and r['model']['worldBounds'][1][1]<=lo[1]+1 for r in candidates),sourceGeometryChanges=0,installationApproved=False,qualification='Complete pinned prepared-sheet metadata scanned inXZ with explicit padding and no height-based omission. Bounds nominate original components only. This does not establish finite contact, source identity, current placement or availability; unknown candidateUIDs staynull.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('prepared_original_neighbour_nomination_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'pinned-prepared-sheet-original-neighbour-bounds-nomination',[Path(__file__),base/a.inventory/'result.json',source_path],result)
 print(dict(uid=a.uid,modelsScanned=len(models),nearbyCandidates=len(candidates),lowerCandidates=result['lowerOriginalCandidates']),flush=True)
if __name__=='__main__':main()
