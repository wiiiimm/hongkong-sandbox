"""Classify exact saved HKUST source/native failures, without waiving any."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-continuous-native-ground-v1-20261015';DOC=B/'government-xl-hkust-native-residual-inventory-v1-20261015';P=B/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014/cached-complete-original-arrays-v1'
def main():
 assert not DOC.exists();prior=read(OLD/'result.json');pins={r['path']:r['sha256'] for r in prior['evidenceRefs']};rows=[];paths=[Path(__file__),OLD/'result.json']
 for uid in ['309822','232155']:
  cp=OLD/f'landsd-{uid}-0.json.gz';ap=P/f'landsd-{uid}-0.json.gz'
  for p in [cp,ap]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];paths.append(p)
  data=read(cp);tri=np.array(read(ap)['completeOrderedOriginalTriangles']);s=data['summary'];faces=data['faces'];bad=s['continuousBelowHalfMetreFaces'];uncovered=s['uncoveredFaces'];bounds=[]
  for i in sorted(set(bad+uncovered)):
   t=tri[i];bounds.append({'sourceFace':i,'position':t.tolist(),'bounds':[t.min(0).tolist(),t.max(0).tolist()],'verticalFace':faces[i].get('verticalFace'),'normalYRatio':faces[i]['normalYRatio'],'belowHalfMetre':i in bad,'groundProjectionCovered':faces[i]['groundProjectionCovered'],'uncoveredProjectionAreaM2':faces[i].get('uncoveredProjectionAreaM2'),'uncoveredProjectionLengthM':faces[i].get('uncoveredProjectionLengthM'),'minimum':faces[i].get('minimum')})
  rows.append({'uid':'landsd/'+uid+':0','belowHalfMetreFaces':bad,'exactVerticalBelowFaces':[i for i in bad if faces[i].get('verticalFace')],'otherBelowFaces':[i for i in bad if not faces[i].get('verticalFace')],'upwardBelowFaces':s['upwardBelowHalfMetreFaces'],'uncoveredCount':len(uncovered),'sumUncoveredFaceProjectionAreaM2':sum(faces[i].get('uncoveredProjectionAreaM2',0) for i in uncovered),'maxUncoveredFaceProjectionAreaM2':max(faces[i].get('uncoveredProjectionAreaM2',0) for i in uncovered),'largestUncoveredFaces':sorted(uncovered,key=lambda i:faces[i].get('uncoveredProjectionAreaM2',0),reverse=True)[:10],'faces':bounds})
 DOC.mkdir();save(DOC/'inventory.json.gz',{'rows':rows,'qualification':'Raw exact classifications only. Summed face areas can overlap. No small-area tolerance, vertical-wall applicability approval, or installation credit.'});summary=[{k:v for k,v in r.items() if k!='faces'} for r in rows];save(DOC/'summary.json',{'rows':summary})
 module('hkust_residual_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-exact-native-failure-type-inventory-v1',paths,{'uids':prior['uids'],'rows':summary,'nextStep':'Use exact residual source/terrain facets to qualify wall-ground source roles and joined-sheet coverage; preserve zero-area/short/finite gaps and unchanged thresholds. No automatic acceptance.'});print(summary,flush=True)
if __name__=='__main__':main()
