"""Measure private terrain-derived estimates for unsurveyed affected BASIC forms."""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from wave_multicore_estimated_bases_v4_20261017 import measure
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','scope','checks']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
 assert all(v.startswith('government-xl-')and'/'not in v for v in vars(a).values())and not out.exists()
 refs=[Path(__file__),HERE/'wave_multicore_estimated_bases_v4_20261017.py'];cache={}
 def take(batch,path):
  if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  assert digest(path.read_bytes())==cache[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,base/a.runtime/'selection.json.gz');runtime=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz');assert len(runtime['rows'])==len(selection['rows'])==1
 forms={b['uid']:b for b in take(a.scope,base/a.scope/'form-obligations.json.gz')};checks=take(a.checks,base/a.checks/'summary.json');ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 proposals=[];retained=[]
 for flagged in checks['flagged']:
  b=forms[flagged['uid']]
  if not(b.get('baseSource')=='terrain-estimated'and b.get('heightSource')=='estimated'and b.get('baseHeightHKPD')is None and b.get('topHeightHKPD')is None and not b.get('modelGeometry')and not b.get('foundationBase')):
   retained.append(dict(uid=b['uid'],reason='surveyed-or-ineligible-basic-fields-unchanged'));continue
  measurement=measure(ground,Polygon(b['rings'][0],b['rings'][1:]));relief=measurement['maximum']-measurement['minimum'];eligible=measurement['uncoveredAreaM2']<1e-8 and abs(measurement['overlapAreaM2'])<1e-8 and relief<b['height']-1.8
  proposals.append(dict(uid=b['uid'],sourceBefore=b,update=dict(base=measurement['minimum']),uniformBaseCandidate=eligible,terrainReliefM=relief,roofClearanceAboveMaximumTerrainM=b['height']-relief,fullCoverage=measurement['uncoveredAreaM2']<1e-8,estimatedHeightUnchanged=True,surveyedFieldsChanged=False,governmentGeometryChanges=0))
  save(out/(b['uid'].split('/')[1]+'-terrain.json'),measurement)
 result=dict(uids=[r['uid']for r in selection['rows']],proposals=proposals,retainedSurveyed=retained,eligiblePrivateEstimates=sum(r['uniformBaseCandidate']for r in proposals),productionChanges=0,governmentGeometryChanges=0,installationApproved=False,publication=False,qualification='Private proposals from complete captured drawn terrain and existing full-footprint coverage/overlap/1.8m clearance gates. No native asset, surveyed base/top, height or footprint changes. Actual production geometry, contact, joint runtime and browser acceptance remain mandatory.')
 save(out/'summary.json',result);module('unsurveyed_basic_ground_proposals',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'source-bound-unsurveyed-basic-private-ground-estimates',refs,result)
 print(dict(proposed=len(proposals),eligible=result['eligiblePrivateEstimates'],retainedSurveyed=len(retained)),flush=True)
if __name__=='__main__':main()
