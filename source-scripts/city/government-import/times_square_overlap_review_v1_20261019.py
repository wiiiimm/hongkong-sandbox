"""Exact original facade overlap interpretation; no geometry or publication change."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-overlap-review-v1-20261019';DOC=BASE/BATCH
ATTR=BASE/'government-xl-times-square-tower254824-burial-attribution-v1-20261019';VIEWS=BASE/'government-xl-times-square-buried-face-views-v1-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [ATTR,VIEWS]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 checks=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  r=read(ATTR/(mode+'.json'));assert r['terrainOnlyFoundation']['fullyBuriedTriangles']==0 and r['compoundStrictFoundationPassed']is False
  assert [f['faceId']for f in r['exactFaces']]==[1092]
  t=np.asarray(r['exactFaces'][0]['vertices']);n=np.cross(t[1]-t[0],t[2]-t[0]);n=n/np.linalg.norm(n);assert abs(n[1])<.01
  checks.append(dict(mode=mode,faceId=1092,normal=n.tolist(),terrainOnlyBuried=0,rawCompoundBuried=1))
 images=[VIEWS/(n+'.png')for n in ['buried-front','buried-reverse']]
 save(DOC/'ROOT-OVERLAP-REVIEW.json',dict(uid='landsd/254824:0',reviewer='Codex ROOT',checks=checks,interpretation='Original face 1092 is a near-vertical tower facade triangle at the podium/tower junction. Front and reverse solid-source exports locate the flagged vertices beside and behind the original podium facade. All four coordinate representations attribute the burial flag to higher original podium surfaces, with zero terrain-only buried faces. Retain this source-authored assembly overlap without changing geometry. This exact-face interpretation does not turn the raw compound measurement into a pass or approve installation.',sourceOverlapInterpretationAccepted=True,imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],installationApproved=False,aiGeometryModelling=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('times_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-times-square-wall-overlap-interpretation',list(dict.fromkeys(refs)),dict(uids=['landsd/254824:0','landsd/233901:0'],faceIds=[1092],interpretationAccepted=True,installationApproved=False))
if __name__=='__main__':main()
